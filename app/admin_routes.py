from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
# Assumimos que estas funções estão no seu arquivo .models
from .models import get_todos_usuarios, adicionar_usuario, buscar_usuario, atualizar_usuario, deletar_usuario 

# Definição do Blueprint com prefixo '/admin'
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ----------------------------------------------------
# ROTA 1: DASHBOARD (LEITURA)
# ----------------------------------------------------
@admin_bp.route('/dashboard')
def dashboard():
    users = get_todos_usuarios()
    
    # Organiza alunos por turma para visualização
    alunos_por_turma = {}
    if 'alunos' in users:
        for mat, dados in users['alunos'].items():
            turma = dados.get('turma', 'Sem Turma')
            if turma not in alunos_por_turma:
                alunos_por_turma[turma] = []
            alunos_por_turma[turma].append({'matricula': mat, **dados})

    # Ordena as turmas
    alunos_por_turma = dict(sorted(alunos_por_turma.items()))

    # O template deve se chamar 'admin_dashboard.html' ou 'admin.html'
    return render_template('admin_dashboard.html', users=users, alunos_por_turma=alunos_por_turma)

# ----------------------------------------------------
# ROTA 2: ADICIONAR USUÁRIO (CRIAÇÃO)
# ----------------------------------------------------
@admin_bp.route('/add_user', methods=['POST'])
def add_user():
    tipo_usuario = request.form.get('tipo_usuario')
    matricula = request.form.get('matricula')
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    
    dados_novo = {
        'password': generate_password_hash(senha),
        'nome': nome
    }

    if tipo_usuario == 'alunos':
        dados_novo['turma'] = request.form.get('turma')
        dados_novo['notas'] = {} 
        dados_novo['faltas'] = {}
        dados_novo['provas'] = {}
    elif tipo_usuario == 'professores':
        disciplinas_raw = request.form.get('disciplinas')
        dados_novo['disciplinas'] = [d.strip() for d in disciplinas_raw.split(',')] if disciplinas_raw else []
    elif tipo_usuario == 'pais':
        dados_novo['filho_matricula'] = request.form.get('filho_matricula')
    
    # Adiciona o usuário usando a função do módulo .models
    if adicionar_usuario(tipo_usuario, matricula, dados_novo):
        flash(f'{tipo_usuario[:-1].capitalize()} cadastrado com sucesso!', 'success')
    else:
        flash('Erro ao adicionar usuário. Verifique os dados.', 'danger')
        
    return redirect(url_for('admin.dashboard'))

# ----------------------------------------------------
# ROTA 3: EDIÇÃO (ATUALIZAÇÃO - GET e POST) - NOVO!
# ----------------------------------------------------
@admin_bp.route('/edit/<user_type>/<user_id>', methods=['GET', 'POST'])
def edit_user(user_type, user_id):
    # Tenta buscar o usuário usando a função do módulo .models
    usuario = buscar_usuario(user_type, user_id)
    
    if not usuario:
        flash(f'Erro: Usuário {user_id} ({user_type}) não encontrado!', 'danger')
        return redirect(url_for('admin.dashboard')) 

    if request.method == 'POST':
        # --- Lógica de submissão do formulário ---
        
        # Cria um dicionário com os dados submetidos no formulário (POST)
        novos_dados = request.form.to_dict()
        
        # 1. TRATAMENTO DE SENHA (SÓ ATUALIZA SE HOUVER NOVA SENHA)
        nova_senha = novos_dados.pop('senha', None)
        if nova_senha:
            novos_dados['password'] = generate_password_hash(nova_senha)
        else:
            # Garante que não salvamos um campo 'senha' vazio no lugar do hash antigo
            if 'password' in novos_dados:
                del novos_dados['password']
            
        # 2. TRATAMENTO DE DISCIPLINAS (PARA PROFESSORES)
        if user_type == 'professores':
            disciplinas_raw = novos_dados.pop('disciplinas', None)
            if disciplinas_raw is not None:
                 novos_dados['disciplinas'] = [d.strip() for d in disciplinas_raw.split(',')]
            
        # 3. TRATAMENTO DE TURMA/FILHO_MATRICULA
        # Se os campos vierem vazios do formulário, removemos a chave, a não ser que seja um dado crítico
        # Aqui assumimos que todos os campos necessários já estão em novos_dados, exceto os que foram tratados acima.
            
        try:
            # Atualiza o usuário no módulo .models
            atualizar_usuario(user_type, user_id, novos_dados)
            flash(f'Cadastro de {usuario["nome"]} ({user_id}) atualizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Erro ao atualizar o cadastro: {e}', 'danger')
            return redirect(url_for('admin.dashboard'))

    # Método GET: Carrega o formulário preenchido (usa o template edit_form.html)
    return render_template('edit_form.html', 
                           usuario=usuario, 
                           user_type=user_type,
                           user_id=user_id) 

# ----------------------------------------------------
# ROTA 4: EXCLUSÃO (DELETE) - NOVO!
# ----------------------------------------------------
@admin_bp.route('/delete/<user_type>/<user_id>', methods=['GET'])
def delete_user(user_type, user_id):
    # Tenta deletar o usuário usando a função do módulo .models
    try:
        if deletar_usuario(user_type, user_id):
            flash(f'Usuário ({user_id}) de tipo "{user_type}" excluído com sucesso!', 'success')
        else:
            flash(f'Erro: Usuário ({user_id}) não encontrado ao tentar excluir!', 'danger')
    except Exception as e:
        flash(f'Erro ao tentar excluir usuário: {e}', 'danger')
    
    # Redireciona de volta para o painel administrativo
    return redirect(url_for('admin.dashboard'))