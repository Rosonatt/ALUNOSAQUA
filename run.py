from app import create_app

# Chama a função create_app() que está no __init__.py para construir a aplicação
app = create_app()

# Inicia o servidor de desenvolvimento
if __name__ == '__main__':
    app.run(debug=True)