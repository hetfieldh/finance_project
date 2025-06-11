# app.py
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required
from datetime import date
import os

# blueprints (rotas)
from routes.user_routes import user_bp
from routes.conta_bancaria_routes import conta_bancaria_bp
from routes.contas_pagar_route import contas_pagar_bp
from routes.crediario_routes import crediario_bp
from routes.movimento_routes import movimento_bp
from routes.transacao_routes import transacao_bp
from routes.tipo_crediario_routes import tipo_crediario_bp
from routes.grupo_crediario_routes import grupo_crediario_bp
from routes.movimento_crediario_routes import movimento_crediario_bp
from routes.extrato_routes import extrato_bp
from routes.despesa_fixa_routes import despesas_fixas_bp

# modelos
from models.user_model import User
from models.conta_bancaria_model import ContaBancaria
from models.contas_pagar_model import ContasPagar
from models.crediario_model import Crediario
from models.movimento_bancario_model import MovimentoBancario
from models.transacao_model import Transacao
from models.tipo_crediario_model import TipoCrediario
from models.grupo_crediario_model import GrupoCrediario
from models.movimento_crediario_model import MovimentoCrediario
from models.despesa_fixa_model import DespesaFixa

# checar e atualizar constraints
from database.db_manager import check_and_update_table_constraints

app = Flask(__name__)
app.config.from_object('config.Config')


# 1. Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message = "Faça login para acessar o sistema."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# 3. Registrar Blueprints (Rotas)
app.register_blueprint(user_bp)
app.register_blueprint(conta_bancaria_bp)
app.register_blueprint(contas_pagar_bp)
app.register_blueprint(crediario_bp)
app.register_blueprint(movimento_bp)
app.register_blueprint(transacao_bp)
app.register_blueprint(tipo_crediario_bp)
app.register_blueprint(grupo_crediario_bp)
app.register_blueprint(movimento_crediario_bp)
app.register_blueprint(extrato_bp)
app.register_blueprint(despesas_fixas_bp)


# 4. Rota Home Principal
@app.route('/')
@login_required
def index():
    current_date = date.today()
    return render_template('index.html', today_date=current_date)


@app.errorhandler(404)
def page_not_found(e):
    flash('A página que você está tentando acessar não existe.', 'danger')
    return render_template('erros/404.html'), 404  # <--- ALTERADO AQUI


@app.errorhandler(500)
def internal_server_error(e):
    flash('Ocorreu um erro interno no servidor. Por favor, tente novamente mais tarde.', 'danger')
    return render_template('erros/500.html'), 500  # <--- ALTERADO AQUI


if __name__ == '__main__':
    with app.app_context():
        User.create_table()
        ContaBancaria.create_table()
        ContasPagar.create_table()
        Crediario.create_table()
        Transacao.create_table()
        MovimentoBancario.create_table()
        TipoCrediario.create_table()
        GrupoCrediario.create_table()
        MovimentoCrediario.create_table()
        DespesaFixa.create_table()
        check_and_update_table_constraints()

    app.run(debug=True)
