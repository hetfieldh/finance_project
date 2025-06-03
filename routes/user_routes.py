from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user_model import User
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps

user_bp = Blueprint('users', __name__)

# --- Decorador para Rotas Apenas de Administrador ---


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash(
                'Acesso negado. Você não tem permissão de administrador para esta ação.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rotas de Usuário ---


@user_bp.route('/list')
@login_required
def list_users():
    # Se o usuário logado for administrador, mostra todos os usuários
    if current_user.is_admin:
        users = User.get_all()
    else:
        # Se não for administrador, mostra apenas o próprio usuário em uma lista
        users = [User.get_by_id(current_user.id)]
    return render_template('users/list.html', users=users)


@user_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required  # Apenas administradores podem adicionar usuários
def add_user():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        is_admin = 'is_admin' in request.form

        if not (login and password and name and email):
            flash('Todos os campos obrigatórios devem ser preenchido!', 'warning')
            return render_template('users/add.html')

        try:
            new_user = User.add(name, email, login, password, is_admin)
            if new_user:
                flash(f'Usuário "{login}" adicionado com sucesso!', 'success')
                return redirect(url_for('users.list_users'))
            else:
                flash(
                    'Não foi possível adicionar o usuário. Verifique os logs do servidor.', 'danger')
        except Exception as e:
            flash(f'Erro ao adicionar usuário: {e}', 'danger')

    # CORRIGIDO: Alterado 'users/add_user.html' para 'users/add.html'
    return render_template('users/add.html')


@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('users.list_users'))

    # Controle de acesso para edição:
    # Admin pode editar qualquer um. Usuário comum só pode editar a si mesmo.
    if not current_user.is_admin and user.id != current_user.id:
        flash('Acesso negado. Você não tem permissão para editar este usuário.', 'danger')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        login = request.form['login']
        password = request.form.get('password')
        name = request.form['name']
        email = request.form['email']
        # Lógica para definir is_admin:
        # Se o usuário logado for admin, ele pode alterar o is_admin do formulário.
        # Caso contrário, o is_admin do usuário editado permanece inalterado.
        is_admin = 'is_admin' in request.form if current_user.is_admin else user.is_admin

        if not (login and name and email):
            flash(
                'Todos os campos obrigatórios (Login, Nome, Email) devem ser preenchidos!', 'warning')
            return render_template('users/edit.html', user=user)

        try:
            updated_user = User.update(
                user_id, name, email, login, password, is_admin)
            if updated_user:
                flash(f'Usuário "{login}" atualizado com sucesso!', 'success')
                return redirect(url_for('users.list_users'))
            else:
                flash(
                    'Não foi possível atualizar o usuário. Verifique os logs do servidor.', 'danger')
        except Exception as e:
            flash(f'Erro ao atualizar usuário: {e}', 'danger')

    return render_template('users/edit.html', user=user)


@user_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    # **VERIFICAÇÃO DE SEGURANÇA: Impedir que o usuário logado se exclua**
    if user_id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('users.list_users'))

    user_to_delete = User.get_by_id(user_id)
    if not user_to_delete:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('users.list_users'))

    # **VERIFICAÇÃO DE SEGURANÇA: Apenas administradores podem excluir outros usuários**
    if not current_user.is_admin:
        flash('Acesso negado. Você não tem permissão para excluir usuários.', 'danger')
        return redirect(url_for('users.list_users'))

    try:
        if User.delete(user_id):
            flash(
                f'Usuário "{user_to_delete.login}" excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir usuário.', 'danger')
    except Exception as e:
        flash(
            f'Ocorreu um erro inesperado ao excluir o usuário: {e}', 'danger')

    return redirect(url_for('users.list_users'))


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.get_by_login(login)

        if user and user.check_password(password):
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login ou senha inválidos.', 'danger')
    return render_template('login.html')


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('users.login'))
