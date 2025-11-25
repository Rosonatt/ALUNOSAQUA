from flask import Flask
from flask_socketio import SocketIO
from .models import NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS

# Inicializa o SocketIO globalmente
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'chave-secreta-do-projeto'

    app.config.update(
        NOTA_MINIMA_APROVACAO_MATERIA=NOTA_MINIMA_APROVACAO_MATERIA,
        MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS
    )

    socketio.init_app(app)

    with app.app_context():
        # --- IMPORTANTE: AS IMPORTAÇÕES DEVEM SER FEITAS AQUI DENTRO ---
        from .routes import main_bp, aluno_bp, pais_bp, professor_bp, psicopedagogo_bp
        from .admin_routes import admin_bp
        
        # AQUI ESTÁ O SEGREDO: Importar os eventos do chat para ativá-los
        from . import chat_events 

        app.register_blueprint(main_bp)
        app.register_blueprint(aluno_bp)
        app.register_blueprint(pais_bp)
        app.register_blueprint(professor_bp)
        app.register_blueprint(psicopedagogo_bp)
        app.register_blueprint(admin_bp)

    return app