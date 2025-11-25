from app import create_app

# O Vercel espera uma variável chamada 'app' no módulo principal.
# Usamos a função de fábrica do seu __init__.py para criá-la.
app = create_app()

# Não precisamos de 'if __name__ == "__main__":' aqui.
# O servidor gunicorn/vercel executará a variável 'app' diretamente.
