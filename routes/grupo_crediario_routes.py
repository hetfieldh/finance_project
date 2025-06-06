# routes/grupo_crediario_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.grupo_crediario_model import GrupoCrediario
from flask_login import login_required, current_user

grupo_crediario_bp = Blueprint(
    'grupo_crediario', __name__, url_prefix='/grupo_crediario')

GRUPO_CREDIARIO_TIPOS = ["Compra", "Estorno"]


@grupo_crediario_bp.route('/')
@login_required
def list_grupo_crediario():
    grupo_crediario = GrupoCrediario.get_all_for_user(current_user.id)
    return render_template('grupo_crediario/list.html', grupo_crediario=grupo_crediario)


@grupo_crediario_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_grupo_crediario():
    if request.method == 'POST':
        grupo = request.form['grupo']
        tipo = request.form['tipo']

        if not (grupo and tipo):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template('grupo_crediario/add.html', tipos_transacao=GRUPO_CREDIARIO_TIPOS)

        if tipo not in GRUPO_CREDIARIO_TIPOS:
            flash('Tipo de Grupo de Crediário inválido.', 'warning')
            return render_template('grupo_crediario/add.html', tipos_transacao=GRUPO_CREDIARIO_TIPOS)

        try:
            GrupoCrediario.add(grupo, tipo, current_user.id)
            flash('Grupo de Crediário adicionado com sucesso!', 'success')
            return redirect(url_for('grupo_crediario.list_grupo_crediario'))
        except ValueError as e:
            flash(f'Erro: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao adicionar o grupo: {e}")
            flash('Ocorreu um erro inesperado ao adicionar o grupo.', 'danger')

    return render_template('grupo_crediario/add.html', tipos_transacao=GRUPO_CREDIARIO_TIPOS)


@grupo_crediario_bp.route('/edit/<int:grupo_id>', methods=['GET', 'POST'])
@login_required
def edit_grupo_crediario(grupo_id):
    grupo = GrupoCrediario.get_by_id(grupo_id, current_user.id)
    if not grupo:
        flash('Grupo não encontrado ou você não tem permissão para editá-lo.', 'danger')
        return redirect(url_for('grupo_crediario.list_grupo_crediario'))

    if request.method == 'POST':
        grupo_nome = request.form['grupo']
        tipo = request.form['tipo']

        if not (grupo_nome and tipo):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template('grupo_crediario/edit.html', grupo=grupo, tipos_transacao=GRUPO_CREDIARIO_TIPOS)

        if tipo not in GRUPO_CREDIARIO_TIPOS:
            flash('Tipo de Grupo de Crediário inválido.',
                  'warning')
            return render_template('grupo_crediario/edit.html', grupo=grupo, tipos_transacao=GRUPO_CREDIARIO_TIPOS)

        try:
            GrupoCrediario.update(grupo_id, grupo_nome, tipo, current_user.id)
            flash('Grupo atualizado com sucesso!', 'success')
            return redirect(url_for('grupo_crediario.list_grupo_crediario'))
        except ValueError as e:
            flash(f'Erro: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao atualizar o grupo: {e}")
            flash('Ocorreu um erro inesperado ao atualizar o grupo.', 'danger')

    return render_template('grupo_crediario/edit.html', grupo=grupo, tipos_transacao=GRUPO_CREDIARIO_TIPOS)


@grupo_crediario_bp.route('/delete/<int:grupo_id>', methods=['POST'])
@login_required
def delete_grupo_crediario(grupo_id):
    grupo = GrupoCrediario.get_by_id(grupo_id, current_user.id)
    if not grupo:
        flash(
            'Grupo não encontrado ou você não tem permissão para excluí-lo.', 'danger')
        return redirect(url_for('grupo_crediario.list_grupo_crediario'))

    if GrupoCrediario.delete(grupo_id, current_user.id):
        flash('Grupo de Crediário excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir o grupo.', 'danger')
    return redirect(url_for('grupo_crediario.list_grupo_crediario'))
