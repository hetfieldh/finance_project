from flask import Flask, render_template
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

# modelos
from models.user_model import User
from models.conta_bancaria_model import ContaBancaria
from models.contas_pagar_model import ContasPagar
from models.crediario_model import Crediario
from models.movimento_bancario_model import MovimentoBancario
from models.transacao_model import Transacao

# checar e atualizar constraints
from database.db_manager import check_and_update_table_constraints

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


# 1. Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# Define a rota para onde o usuário será redirecionado se não estiver logado
login_manager.login_view = 'users.login'
login_manager.login_message = "Faça login para acessar o sistema."
login_manager.login_message_category = "info"

# Callback para recarregar o objeto User do ID do usuário armazenado na sessão


@login_manager.user_loader
def load_user(user_id):
    # Flask-Login espera que esta função retorne um objeto User ou None se o ID não for válido.
    return User.get_by_id(user_id)


# 2. Criar tabelas se não existirem
# Este bloco é executado uma vez quando o aplicativo é carregado.
# A ordem das chamadas create_table() é importante devido às chaves estrangeiras.
with app.app_context():
    User.create_table()            # Tabela de usuários (pai de muitas)
    ContaBancaria.create_table()   # Tabela de contas bancárias (depende de users)
    ContasPagar.create_table()     # Tabela de contas a pagar
    Crediario.create_table()       # Tabela de crediários
    Transacao.create_table()       # Tabela de tipos de transação
    MovimentoBancario.create_table()  # Tabela de movimentos bancários

    # Chama a função para verificar e adicionar colunas ou constraints se necessário.
    # Útil para atualizações de esquema sem apagar o banco de dados.
    check_and_update_table_constraints()


# 3. Registrar Blueprints (Rotas)
# Isso conecta as rotas definidas nos seus arquivos de rotas (blueprints) ao aplicativo principal.
app.register_blueprint(user_bp)
app.register_blueprint(conta_bancaria_bp)
app.register_blueprint(contas_pagar_bp)
app.register_blueprint(crediario_bp)
app.register_blueprint(movimento_bp)
app.register_blueprint(transacao_bp)


# 4. Rota Home Principal
# Esta é a rota para a página inicial do seu aplicativo.
@app.route('/')
# Esta rota exige que o usuário esteja logado para ser acessada.
@login_required
def index():
    # Obtém a data atual para passar ao template, se necessário.
    current_date = date.today()
    return render_template('index.html', today_date=current_date)


if __name__ == '__main__':
    # Quando o script é executado diretamente, o servidor de desenvolvimento do Flask é iniciado.
    # debug=True ativa o modo de depuração, que inclui o recarregamento automático do servidor
    # ao detectar mudanças no código e um depurador interativo.
    app.run(debug=True)
