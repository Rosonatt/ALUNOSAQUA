from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import uuid
import calendar
from datetime import datetime, timedelta
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except locale.Error:
        print("Locale pt_BR não encontrado.")

# Importa o salvar_banco
from .models import USERS, DENUNCIAS, calcular_dados_aluno, NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS, HOLIDAYS_2025, salvar_banco

main_bp = Blueprint('main', __name__)
aluno_bp = Blueprint('aluno', __name__, url_prefix='/aluno')
pais_bp = Blueprint('pais', __name__, url_prefix='/pais')
professor_bp = Blueprint('professor', __name__, url_prefix='/professor')
psicopedagogo_bp = Blueprint('psicopedagogo', __name__, url_prefix='/psicopedagogo')


@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/informacoes-cadastro')
def informacoes_cadastro():
    return render_template('informacoes_cadastro.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type_selected = request.form['user_type']
        username = request.form['username'].strip()
        password = request.form['password']

        admin_user = USERS['admins'].get(username)
        if admin_user and check_password_hash(admin_user['password'], password):
            session['user_type'] = 'admin'
            session['username'] = username
            session['display_name'] = admin_user['nome']
            return redirect(url_for('admin.dashboard'))

        user_map = {
            'aluno': ('alunos', 'aluno.dashboard'), 
            'pais': ('pais', 'pais.dashboard'), 
            'professor': ('professores', 'professor.dashboard'), 
            'psicopedagogo': ('psicopedagogos', 'psicopedagogo.dashboard'),
            'admin': ('admins', 'admin.dashboard')
        }
        
        if user_type_selected in user_map:
            cat, endp = user_map[user_type_selected]
            user = USERS[cat].get(username)
            if user and check_password_hash(user.get('password'), password):
                session['user_type'] = user_type_selected
                session['username'] = username
                session['display_name'] = user['nome']
                session['user_id'] = username 
                return redirect(url_for(endp))
        
        flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@aluno_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    aluno = USERS['alunos'].get(session['username'])
    if not aluno: return redirect(url_for('main.logout')) 
    return render_template('aluno_dashboard.html', aluno=aluno)

@aluno_bp.route('/notas')
def notas():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    aluno_data = USERS['alunos'].get(session['username'])
    if not aluno_data: return redirect(url_for('main.logout'))
    return render_template('aluno_notas.html', aluno=aluno_data, dados_calculados=calcular_dados_aluno(aluno_data), config={'NOTA_MINIMA_APROVACAO_MATERIA': NOTA_MINIMA_APROVACAO_MATERIA})

@aluno_bp.route('/presenca')
def presenca():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    aluno_data = USERS['alunos'].get(session['username'])
    if not aluno_data: return redirect(url_for('main.logout'))

    try:
        ano_atual = int(request.args.get('ano', datetime.now().year))
        mes_atual = int(request.args.get('mes', datetime.now().month))
        if not 1 <= mes_atual <= 12: raise ValueError("Mês inválido")
    except (ValueError, TypeError):
        ano_atual, mes_atual = datetime.now().year, datetime.now().month

    primeiro_dia_do_mes = datetime(ano_atual, mes_atual, 1)
    mes_anterior_data = primeiro_dia_do_mes - timedelta(days=1)
    ano_anterior, mes_anterior = mes_anterior_data.year, mes_anterior_data.month
    _, ultimo_dia_num = calendar.monthrange(ano_atual, mes_atual)
    ultimo_dia_do_mes = datetime(ano_atual, mes_atual, ultimo_dia_num)
    mes_seguinte_data = ultimo_dia_do_mes + timedelta(days=1)
    ano_seguinte, mes_seguinte = mes_seguinte_data.year, mes_seguinte_data.month

    dados = calcular_dados_aluno(aluno_data)
    disciplinas_aluno = sorted(aluno_data.get('notas', {}).keys())
    default_discipline = disciplinas_aluno[0] if disciplinas_aluno else 'Matemática'
    disciplina_sel = request.args.get('disciplina', default_discipline)
    
    faltas_disciplina_total = dados['detalhe_faltas_por_materia'].get(disciplina_sel, {'total': 0, 'justificadas': 0})
    num_faltas_disciplina = faltas_disciplina_total['total']
    num_justificadas_disciplina = faltas_disciplina_total['justificadas']
    num_nao_justificadas_disciplina = num_faltas_disciplina - num_justificadas_disciplina
    status_disciplina_faltas = 'REPROVADO POR FALTAS' if num_nao_justificadas_disciplina > MAX_FALTAS_PERMITIDAS else 'APROVADO'
    
    subject_stats={'total_faltas': num_faltas_disciplina, 'justificadas': num_justificadas_disciplina, 'nao_justificadas': num_nao_justificadas_disciplina, 'status': status_disciplina_faltas}
    
    cal = calendar.Calendar()
    cal.setfirstweekday(calendar.SUNDAY)
    semanas_do_mes = cal.monthdatescalendar(ano_atual, mes_atual)
    todas_as_faltas = set()
    for faltas_obj_list in aluno_data.get('faltas', {}).values():
        for falta_dict in faltas_obj_list:
            todas_as_faltas.add(falta_dict['date'])
    faltas_disciplina = set()
    if disciplina_sel:
        for falta_dict in aluno_data.get('faltas', {}).get(disciplina_sel, []):
            faltas_disciplina.add(falta_dict['date'])
    provas_disciplina = aluno_data.get('provas', {}).get(disciplina_sel, [])
    
    proximos_feriados = []
    hoje_str = datetime.now().strftime('%Y-%m-%d')
    for data_str in HOLIDAYS_2025:
        if data_str >= hoje_str:
            try:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                nome_feriado = data_obj.strftime('%d/%m/%Y (%A)') 
                proximos_feriados.append({'data': data_obj, 'nome': nome_feriado})
            except ValueError: continue
    proximos_feriados_ordenados = sorted(proximos_feriados, key=lambda x: x['data'])[:5]
    
    return render_template('aluno_presenca.html', aluno=aluno_data, dados_calculados=dados, semanas=semanas_do_mes, mes_atual=mes_atual, ano_atual=ano_atual, hoje=datetime.now().date(), chart_data={'presente': 100 - dados['porcentagem_faltas'], 'ausente': dados['porcentagem_faltas']}, ano_anterior=ano_anterior, mes_anterior=mes_anterior, ano_seguinte=ano_seguinte, mes_seguinte=mes_seguinte, todas_as_faltas=todas_as_faltas, dias_nao_letivos=HOLIDAYS_2025, proximos_feriados=proximos_feriados_ordenados, MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS, faltas_disciplina=faltas_disciplina, provas_disciplina=provas_disciplina, disciplina_selecionada=disciplina_sel, disciplinas_aluno=disciplinas_aluno, subject_stats=subject_stats)

@aluno_bp.route('/denunciar', methods=['GET', 'POST'])
def denunciar():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    if request.method == 'POST':
        den_id = str(uuid.uuid4())
        aluno_nome = USERS['alunos'].get(session['username'], {}).get('nome', session['username'])
        denuncia_data = {
            'id': den_id, 'serial': den_id.split('-')[0].upper(), 'aluno_matricula': session['username'], 'aluno_nome': aluno_nome,
            'status': 'aberta', 'urgencia': 'não classificada', 'descricao': request.form.get('descricao', 'Não preenchido'),
            'agressor_tipo': request.form.getlist('agressor_tipo[]'), 'natureza': request.form.getlist('natureza[]'), 'frequencia': request.form.get('frequencia'),
            'local': request.form.getlist('local[]'), 'reportado': request.form.get('reportado'), 'vitima_conhecimento': request.form.get('vitima_conhecimento'),
            'evidencia': request.form.get('evidencia'), 'gravidade': request.form.get('gravidade'), 'expectativa': request.form.get('expectativa', 'Não preenchido')
        }
        DENUNCIAS[den_id] = denuncia_data
        salvar_banco() # SALVA
        flash('Denúncia enviada com sucesso!', 'success')
        return redirect(url_for('aluno.dashboard'))
    return render_template('aluno_denunciar.html')

@pais_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'pais': return redirect(url_for('main.login'))
    filho_matricula = USERS['pais'].get(session['username'], {}).get('filho_matricula', '').strip()
    filho = USERS['alunos'].get(filho_matricula)
    if not filho: return redirect(url_for('main.logout'))
    return render_template('pais_dashboard.html', filho=filho, dados_calculados=calcular_dados_aluno(filho), MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS)

@professor_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'professor': return redirect(url_for('main.login'))
    prof_data = USERS['professores'].get(session['username'])
    if not prof_data: return redirect(url_for('main.logout'))
    disciplinas = prof_data['disciplinas']
    if not disciplinas:
        flash('Seu perfil não tem disciplinas registradas.', 'warning')
        return render_template('professor_dashboard.html', alunos=[], disciplinas=[], disciplina_selecionada='N/A', NOTA_MINIMA=NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS)

    disciplina_sel = request.args.get('disciplina', disciplinas[0])
    alunos_filtrados = []
    for matricula, aluno_data in USERS['alunos'].items():
        dados = calcular_dados_aluno(aluno_data)
        info_disciplina = dados['medias_materias'].get(disciplina_sel, {})
        aluno_info = {
            'matricula': matricula, 'nome': aluno_data['nome'],
            'nota1': info_disciplina.get('nota1', 'N/A'), 'nota2': info_disciplina.get('nota2', 'N/A'),
            'media': info_disciplina.get('media', 'N/A'), 'faltas_nao_justificadas': dados['num_nao_justificadas'], 'faltas': dados['faltas_por_materia'].get(disciplina_sel, 0)
        }
        alunos_filtrados.append(aluno_info)
    return render_template('professor_dashboard.html', alunos=alunos_filtrados, disciplinas=disciplinas, disciplina_selecionada=disciplina_sel, NOTA_MINIMA=NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS)

@professor_bp.route('/atualizar-dados/<matricula>', methods=['GET', 'POST'])
def atualizar_dados(matricula):
    if session.get('user_type') != 'professor': return redirect(url_for('main.login'))
    prof_data = USERS['professores'].get(session['username'])
    disciplina = request.args.get('disciplina')
    if not disciplina or disciplina not in prof_data['disciplinas']:
        flash('Erro de permissão ou disciplina.', 'danger')
        return redirect(url_for('professor.dashboard'))
    aluno_data = USERS['alunos'].get(matricula)
    
    if request.method == 'POST':
        n1_str, n2_str = request.form.get(f'nota_{disciplina}_1'), request.form.get(f'nota_{disciplina}_2')
        if n1_str and n2_str:
            if 'notas' not in aluno_data: aluno_data['notas'] = {}
            aluno_data['notas'][disciplina] = [float(n1_str), float(n2_str)]
            flash(f'Notas atualizadas.', 'success')

        num_faltas_count = int(request.form.get('num_faltas_count', 0))
        novas_faltas = []
        for i in range(num_faltas_count):
            data_str = request.form.get(f'falta_data_{i}', '').strip()
            is_justified = request.form.get(f'falta_justificada_{i}') == 'True'
            if data_str:
                try:
                    datetime.strptime(data_str, '%Y-%m-%d')
                    novas_faltas.append({'date': data_str, 'justified': is_justified})
                except: pass
        
        aluno_data.setdefault('faltas', {})[disciplina] = novas_faltas
        salvar_banco() # SALVA
        flash(f'Dados salvos com sucesso.', 'success')
        return redirect(url_for('professor.dashboard', disciplina=disciplina))
        
    faltas_da_disciplina = aluno_data.get('faltas', {}).get(disciplina, [])
    if disciplina not in aluno_data.get('notas', {}):
        aluno_data.setdefault('notas', {})[disciplina] = []
    return render_template('professor_atualizar_dados.html', aluno=aluno_data, matricula=matricula, disciplina=disciplina, faltas_da_disciplina=faltas_da_disciplina)

@psicopedagogo_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    denuncias_abertas = [{'aluno_nome': USERS['alunos'].get(d['aluno_matricula'], {'nome': d['aluno_matricula']})['nome'], **d} for id, d in DENUNCIAS.items() if d['status'] == 'aberta']
    denuncias_ordenadas = sorted(denuncias_abertas, key=lambda d: (d['urgencia'] != 'alta', d['urgencia'] != 'média', d['urgencia'] != 'baixa'))
    return render_template('psicopedagogo_dashboard.html', denuncias=denuncias_ordenadas, alunos=USERS['alunos'])

@psicopedagogo_bp.route('/definir_urgencia/<denuncia_id>', methods=['POST'])
def definir_urgencia(denuncia_id):
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    if denuncia_id in DENUNCIAS:
        DENUNCIAS[denuncia_id]['urgencia'] = request.form['urgencia']
        salvar_banco() # SALVA
        flash('Urgência atualizada.', 'success')
    return redirect(url_for('psicopedagogo.dashboard'))

@psicopedagogo_bp.route('/denuncia/<denuncia_id>')
def denuncia_detalhe(denuncia_id):
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    denuncia = DENUNCIAS.get(denuncia_id)
    if not denuncia: return redirect(url_for('psicopedagogo.dashboard'))
    aluno = USERS['alunos'].get(denuncia['aluno_matricula'], {})
    return render_template('denuncia_detalhe.html', denuncia_id=denuncia_id, denuncia=denuncia, aluno=aluno, dados_calculados=calcular_dados_aluno(aluno) if aluno else {})

@psicopedagogo_bp.route('/fechar_caso/<denuncia_id>', methods=['POST'])
def fechar_caso(denuncia_id):
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    if denuncia_id in DENUNCIAS:
        DENUNCIAS[denuncia_id]['status'] = 'fechada'
        salvar_banco() # SALVA
        flash('Caso fechado.', 'success')
    return redirect(url_for('psicopedagogo.dashboard'))