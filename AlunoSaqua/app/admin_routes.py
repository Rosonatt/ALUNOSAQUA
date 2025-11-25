from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from .models import USERS, adicionar_usuario, get_todos_usuarios

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

    return render_template('admin_dashboard.html', users=users, alunos_por_turma=alunos_por_turma)

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
    
    if adicionar_usuario(tipo_usuario, matricula, dados_novo):
        flash(f'{tipo_usuario[:-1].capitalize()} cadastrado com sucesso!', 'success')
    else:
        flash('Erro ao adicionar usuário. Verifique os dados.', 'danger')
        
    return redirect(url_for('admin.dashboard'))