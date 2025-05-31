from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user_model import User
from psycopg.errors import UniqueViolation
from flask_login import login_user, logout_user, login_required, current_user

user_bp = Blueprint('users', __name__, url_prefix='/users')

# Nova Rota para Login


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Se o usuário já estiver logado, redireciona para a home
        return redirect(url_for('index'))

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        user = User.get_by_login(login)  # Busca o usuário pelo login
        if user and user.check_password(password):  # Verifica a senha
            login_user(user)  # Faz o login do usuário
            flash('Login bem-sucedido!', 'success')
            # Redireciona para a página de onde o usuário veio (se houver) ou para a home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login ou senha incorretos.', 'danger')

    return render_template('login.html')

# Nova Rota para Logout


@user_bp.route('/logout')
@login_required  # Garante que apenas usuários logados podem acessar esta rota
def logout():
    logout_user()  # Faz o logout do usuário
    flash('Você foi desconectado.', 'success')
    # Redireciona para a página de login
    return redirect(url_for('users.login'))

# Proteger as rotas de gerenciamento de usuários


@user_bp.route('/')
@login_required  # Apenas usuários logados podem ver a lista de usuários
def list_users():
    users = User.get_all()
    return render_template('users/list.html', users=users)


@user_bp.route('/add', methods=['GET', 'POST'])
@login_required  # Apenas usuários logados podem adicionar usuários
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        login = request.form['login']
        password = request.form['password']

        if not (name and email and login and password):
            flash('Todos os campos são obrigatórios!', 'warning')
        else:
            try:
                new_user = User.add(name, email, login, password)
                if new_user:
                    flash('Usuário adicionado com sucesso!', 'success')
                    return redirect(url_for('users.list_users'))
            except ValueError as e:
                flash(str(e), 'danger')  # Captura a mensagem de erro do modelo
            except Exception as e:
                print(f"Erro inesperado ao adicionar usuário: {e}")
                flash('Ocorreu um erro inesperado ao adicionar o usuário.', 'danger')
    return render_template('users/add.html')


@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required  # Apenas usuários logados podem editar usuários
def edit_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        login = request.form['login']
        # Use .get() para campos opcionais
        new_password = request.form.get('password')

        if not (name and email and login):
            flash('Nome, Email e Login são obrigatórios!', 'warning')
        else:
            try:
                # Passa a nova senha (pode ser None) para o método update
                updated_user = User.update(
                    user_id, name, email, login, new_password)
                if updated_user:
                    flash('Usuário atualizado com sucesso!', 'success')
                    return redirect(url_for('users.list_users'))
            except ValueError as e:
                flash(str(e), 'danger')
            except Exception as e:
                print(f"Erro inesperado ao atualizar usuário: {e}")
                flash('Ocorreu um erro inesperado ao atualizar o usuário.', 'danger')
    return render_template('users/edit.html', user=user)


@user_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required  # Apenas usuários logados podem excluir usuários
def delete_user(user_id):
    if User.delete(user_id):
        flash('Usuário excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir usuário.', 'danger')
    return redirect(url_for('users.list_users'))
