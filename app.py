from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import os

# Importe os blueprints (rotas)
from routes.user_routes import user_bp
from routes.conta_routes import conta_bp
from routes.contas_pagar_route import contas_pagar_bp
from routes.crediario_routes import crediario_bp
from models.user_model import User  # Importe seu modelo de usuário

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

login_manager.login_message = "Faça login para acessar o sitema."
login_manager.login_message_category = "info"

# Callback para recarregar o objeto User do ID do usuário armazenado na sessão


@login_manager.user_loader
def load_user(user_id):
    # Flask-Login espera que esta função retorne um objeto User
    # ou None se o ID não for válido.
    return User.get_by_id(user_id)


# Registrar Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(conta_bp)
app.register_blueprint(contas_pagar_bp)
app.register_blueprint(crediario_bp)

# Rota Home


@app.route('/')
@login_required
def index():
    # Se o usuário chegar aqui, significa que ele está logado.
    # O Flask-Login já cuida do redirecionamento para o login se não estiver.
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
