import json
import os
from werkzeug.security import generate_password_hash

# --- ARQUIVO DO BANCO DE DADOS ---
DB_FILE = 'banco_de_dados.json'

# --- CONFIGURAÇÕES GLOBAIS ---
MAX_FALTAS_PERMITIDAS = 4
TOTAL_AULAS_PADRAO = 100
NOTA_MINIMA_APROVACAO_MATERIA = 7

HOLIDAYS_2025 = [
    '2025-01-01', '2025-03-03', '2025-03-04', '2025-03-05', 
    '2025-04-18', '2025-04-21', '2025-05-01', '2025-06-19', 
    '2025-09-08', '2025-11-15', '2025-12-25',
]

# --- DADOS INICIAIS (SEED) ---
DADOS_PADRAO = {
    'users': {
        'alunos': {
            '202411251': {'password': generate_password_hash('aluno'), 'nome': 'Rosonatt Ferreira Ramos', 'turma': '9A', 'notas': {'Matemática': [8, 7], 'Português': [9, 8], 'História': [7, 7], 'Ciências': [10, 9]}, 'faltas': {'Matemática': [{'date': '2025-10-01', 'justified': False}], 'Português': [{'date': '2025-10-02', 'justified': False}, {'date': '2025-09-15', 'justified': False}]}, 'provas': {'Matemática': ['2025-10-06']}},
            '202411281': {'password': generate_password_hash('aluno'), 'nome': 'Ryan Guiwison', 'turma': '8B', 'notas': {'Matemática': [5, 4], 'Português': [6, 7.5], 'Artes': [5, 5]}, 'faltas': {'Matemática': [{'date': '2025-10-03', 'justified': False}, {'date': '2025-10-06', 'justified': False}, {'date': '2025-10-07', 'justified': False}], 'Português': [{'date': '2025-09-08', 'justified': False}, {'date': '2025-09-09', 'justified': False}], 'Artes': [{'date': '2025-08-10', 'justified': False}, {'date': '2025-08-15', 'justified': False}, {'date': '2025-08-16', 'justified': False}, {'date': '2025-08-17', 'justified': False}, {'date': '2025-08-18', 'justified': False}]}, 'provas': {}},
            '202411333': {'password': generate_password_hash('aluno'), 'nome': 'Bruno Alves', 'turma': '7C', 'notas': {'Artes': [5, 4], 'Português': [7, 6.5]}, 'faltas': {'Artes': [{'date': '2025-09-11', 'justified': False}]}, 'provas': {}},
            '202411325': {'password': generate_password_hash('aluno'), 'nome': 'Natalia Crys Cardoso', 'turma': '9A', 'notas': {'Inglês': [8.5, 9], 'Física': [6.5, 7.5]}, 'faltas': {}, 'provas': {}},
            '202411265': {'password': generate_password_hash('aluno'), 'nome': 'Kevin Paula', 'turma': '6D', 'notas': {'Química': [7, 7], 'Literatura': [8, 6]}, 'faltas': {'Química': [{'date': '2025-09-05', 'justified': False}, {'date': '2025-09-12', 'justified': False}, {'date': '2025-09-19', 'justified': False}]}, 'provas': {}},
            '202411271': {'password': generate_password_hash('aluno'), 'nome': 'Raissa Leite', 'turma': '5E', 'notas': {'Sociologia': [9, 8.5], 'Filosofia': [7, 7]}, 'faltas': {'Sociologia': [{'date': '2025-09-23', 'justified': False}]}, 'provas': {}},
            '55667': {'password': generate_password_hash('aluno'), 'nome': 'João Candia', 'turma': '4F', 'notas': {'Educação Física': [9.5, 9], 'Biologia': [6, 6.5]}, 'faltas': {}, 'provas': {'Biologia': ['2025-09-26']}},
            '66778': {'password': generate_password_hash('aluno'), 'nome': 'Ronald Carvalho', 'turma': '3G', 'notas': {'Matemática': [7, 7], 'Português': [7.5, 7.5]}, 'faltas': {'Matemática': [{'date': '2025-09-04', 'justified': False}], 'Português': [{'date': '2025-09-18', 'justified': False}]}, 'provas': {}}
        },
        'pais': {
            'pai_rosonatt': {'password': generate_password_hash('pai'), 'nome': 'Responsável Rosonatt', 'filho_matricula': '202411251'},
            'pai_ryan': {'password': generate_password_hash('pai2'), 'nome': 'Responsável Ryan', 'filho_matricula': '202411281'},
            'pai_bruno': {'password': generate_password_hash('mae'), 'nome': 'Responsável Bruno', 'filho_matricula': '202411333'},
            'mae_natalia': {'password': generate_password_hash('pais'), 'nome': 'Responsável Natalia', 'filho_matricula': '202411325'},
            'pai_kevin': {'password': generate_password_hash('pais2'), 'nome': 'Responsável Kevin', 'filho_matricula': '202411265'},
            'mae_raissa': {'password': generate_password_hash('pais3'), 'nome': 'Responsável Raissa', 'filho_matricula': '202411271'},
            'pai_joao': {'password': generate_password_hash('pais4'), 'nome': 'Responsável João', 'filho_matricula': '55667'},
            'mae_ronald': {'password': generate_password_hash('pais5'), 'nome': 'Responsável Ronald', 'filho_matricula': '66778'},
        },
        'professores': {
            '202411000': {'password': generate_password_hash('prof'), 'nome': 'Lucas', 'disciplinas': ['Matemática', 'Ciências']},
            '202411111': {'password': generate_password_hash('prof'), 'nome': 'André', 'disciplinas': ['Português', 'História']},
            '202411222': {'password': generate_password_hash('prof'), 'nome': 'Diego', 'disciplinas': ['Artes', 'Educação Física']},
            '202411333': {'password': generate_password_hash('prof'), 'nome': 'Gioliano', 'disciplinas': ['Geografia', 'Inglês']}
        },
        'psicopedagogos': {
            'psi_joana': {'password': generate_password_hash('psi'), 'nome': 'Joana'},
            'psi_pedro': {'password': generate_password_hash('psi2'), 'nome': 'Pedro'},
            'coord_educ': {'password': generate_password_hash('coord'), 'nome': 'Coordenadora Maria'},
            'sup_psi': {'password': generate_password_hash('sup'), 'nome': 'Supervisor Antonio'},
        },
        'admins': {
            'admin': {'password': generate_password_hash('admin'), 'nome': 'Administrador Geral'}
        }
    },
    'denuncias': {},
    'chat_messages': {}
}

# Variáveis globais que a aplicação vai usar
USERS = {}
DENUNCIAS = {}
CHAT_MESSAGES = {}

# --- SISTEMA DE PERSISTÊNCIA (BANCO DE DADOS) ---
def carregar_banco():
    """Carrega os dados do arquivo JSON ou cria se não existir."""
    global USERS, DENUNCIAS, CHAT_MESSAGES
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                USERS = dados.get('users', {})
                DENUNCIAS = dados.get('denuncias', {})
                CHAT_MESSAGES = dados.get('chat_messages', {})
                print(">>> Banco de dados carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar banco: {e}. Usando padrão.")
            USERS = DADOS_PADRAO['users']
            DENUNCIAS = DADOS_PADRAO['denuncias']
            CHAT_MESSAGES = DADOS_PADRAO['chat_messages']
    else:
        print(">>> Criando novo banco de dados...")
        USERS = DADOS_PADRAO['users']
        DENUNCIAS = DADOS_PADRAO['denuncias']
        CHAT_MESSAGES = DADOS_PADRAO['chat_messages']
        salvar_banco()

def salvar_banco():
    """Salva o estado atual das variáveis no arquivo JSON."""
    dados = {
        'users': USERS,
        'denuncias': DENUNCIAS,
        'chat_messages': CHAT_MESSAGES
    }
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro crítico ao salvar banco: {e}")

# Inicializa o banco ao importar este arquivo
carregar_banco()

# --- FUNÇÕES AUXILIARES (Lógica de Cálculo) ---
def calcular_dados_aluno(aluno_data):
    # ... (Mantenha toda a sua lógica de cálculo de faltas e notas aqui) ...
    # O código é grande, então mantive a estrutura original, assumindo que está correta.
    
    faltas_por_materia = {}
    num_justificadas_total = 0
    num_faltas_total = 0
    porcentagem_faltas = 0
    detalhe_faltas_por_materia = {}
    
    for materia, faltas_list in aluno_data.get('faltas', {}).items():
        contagem_faltas_materia = len(faltas_list)
        contagem_justificadas_materia = 0

        for falta in faltas_list:
            if isinstance(falta, dict) and falta.get('justified', False):
                contagem_justificadas_materia += 1

        detalhe_faltas_por_materia[materia] = {
            'total': contagem_faltas_materia,
            'justificadas': contagem_justificadas_materia
        }
        
        faltas_por_materia[materia] = contagem_faltas_materia
        num_faltas_total += contagem_faltas_materia
        num_justificadas_total += contagem_justificadas_materia
        
    num_nao_justificadas = num_faltas_total - num_justificadas_total
    status_faltas = 'REPROVADO POR FALTAS' if num_nao_justificadas > MAX_FALTAS_PERMITIDAS else 'APROVADO'
    
    materia_mais_faltas = None
    maior_num_faltas = 0
    if detalhe_faltas_por_materia:
        materia_mais_faltas = max(detalhe_faltas_por_materia, key=lambda m: detalhe_faltas_por_materia[m]['total'])
        maior_num_faltas = detalhe_faltas_por_materia[materia_mais_faltas]['total']

    porcentagem_faltas = (num_faltas_total / TOTAL_AULAS_PADRAO) * 100 if TOTAL_AULAS_PADRAO > 0 else 0
    
    medias_materias = {}
    materias_reprovadas = []
    for disciplina, notas_list in aluno_data.get('notas', {}).items():
        if isinstance(notas_list, list) and len(notas_list) == 2:
            media_notas = sum(notas_list)/2
            status_materia = 'APROVADO' if media_notas >= NOTA_MINIMA_APROVACAO_MATERIA else 'REPROVADO'
            if status_materia == 'REPROVADO': materias_reprovadas.append(disciplina)
            medias_materias[disciplina] = {'nota1': notas_list[0], 'nota2': notas_list[1], 'media': round(media_notas, 1), 'status': status_materia}
        else:
            nota1 = notas_list[0] if isinstance(notas_list, list) and len(notas_list) > 0 else 'N/A'
            medias_materias[disciplina] = {'nota1': nota1, 'nota2': 'N/A', 'media': 'N/A', 'status': 'PENDENTE'}
    
    status_geral_notas = 'Reprovado' if materias_reprovadas else 'Aprovado'
    status_final = 'APROVADO'
    if 'REPROVADO' in status_faltas or status_geral_notas == 'Reprovado': 
        status_final = 'REPROVADO'
        
    return {
        'num_faltas': num_faltas_total, 
        'num_justificadas': num_justificadas_total, 
        'num_nao_justificadas': num_nao_justificadas, 
        'faltas_por_materia': faltas_por_materia, 
        'detalhe_faltas_por_materia': detalhe_faltas_por_materia, 
        'porcentagem_faltas': round(porcentagem_faltas, 2),
        'status_faltas': status_faltas, 'medias_materias': medias_materias,
        'materias_reprovadas': materias_reprovadas, 'status_geral_notas': status_geral_notas,
        'status_final_aluno': status_final,
        'materia_mais_faltas': materia_mais_faltas,
        'maior_num_faltas': maior_num_faltas
    }

def adicionar_usuario(tipo, matricula, dados):
    if tipo in USERS:
        USERS[tipo][matricula] = dados
        salvar_banco() # SALVA NO DISCO
        return True
    return False

def get_todos_usuarios():
    return USERS

# --------------------------------------------------------------------------
# --- FUNÇÕES DE CRUD PARA AS ROTAS (BUSCAR, ATUALIZAR E DELETAR) - NOVO! ---
# --------------------------------------------------------------------------

def buscar_usuario(user_type, user_id):
    """ Retorna os dados de um usuário específico ou None se não encontrado. """
    if user_type in USERS and user_id in USERS[user_type]:
        # Retorna uma cópia para evitar alterações acidentais
        return USERS[user_type][user_id].copy() 
    return None

def atualizar_usuario(user_type, user_id, novos_dados):
    """ Atualiza os dados de um usuário no banco e salva no disco. """
    if user_type in USERS and user_id in USERS[user_type]:
        # Atualiza os dados do usuário com os novos dados
        USERS[user_type][user_id].update(novos_dados)
        salvar_banco()
        return True
    return False

def deletar_usuario(user_type, user_id):
    """ Remove um usuário do banco de dados e salva no disco. """
    if user_type in USERS and user_id in USERS[user_type]:
        del USERS[user_type][user_id]
        salvar_banco()
        return True
    return False