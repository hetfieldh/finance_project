from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import os

# Importe os blueprints (rotas)
from routes.user_routes import user_bp
from routes.conta_bancaria_routes import conta_bancaria_bp
from routes.contas_pagar_route import contas_pagar_bp
from routes.crediario_routes import crediario_bp
from routes.movimento_routes import movimento_bp

# Importe os modelos
from models.user_model import User
from models.conta_bancaria_model import ContaBancaria
from models.contas_pagar_model import ContasPagar
from models.crediario_model import Crediario
from models.movimento_bancario_model import MovimentoBancario

# Importe para checar e atualizar constraints
from database.db_manager import check_and_update_table_constraints

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


# 1. Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message = "Faça login para acessar o sistema."
login_manager.login_message_category = "info"

# Callback para recarregar o objeto User do ID do usuário armazenado na sessão


@login_manager.user_loader
def load_user(user_id):
    # Flask-Login espera que esta função retorne um objeto User
    # ou None se o ID não for válido.
    return User.get_by_id(user_id)


# 2. Criar tabelas se não existirem
# A ordem é importante para chaves estrangeiras (ex: users antes de contas, contas antes de movimentos)
with app.app_context():
    User.create_table()
    ContaBancaria.create_table()
    ContasPagar.create_table()
    Crediario.create_table()
    MovimentoBancario.create_table()
    check_and_update_table_constraints()

# 3. Registrar Blueprints (Rotas)
# Isso conecta as rotas definidas nos seus arquivos de rotas ao aplicativo principal.
app.register_blueprint(user_bp)
app.register_blueprint(conta_bancaria_bp)
app.register_blueprint(contas_pagar_bp)
app.register_blueprint(crediario_bp)
app.register_blueprint(movimento_bp)

# 4. Rota Home Principal


@app.route('/')
@login_required  # Esta rota exige que o usuário esteja logado
def index():
    # Se o usuário chegar aqui, significa que ele está logado.
    return render_template('index.html')


if __name__ == '__main__':
    print("Executando o aplicativo Flask...")
    app.run(debug=True)
