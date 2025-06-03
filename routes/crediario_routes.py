from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.crediario_model import Crediario
from models.tipo_crediario_model import TipoCrediario
from flask_login import login_required, current_user
from psycopg.errors import UniqueViolation

crediario_bp = Blueprint('crediarios', __name__, url_prefix='/crediarios')


@crediario_bp.route('/')
@login_required
def list_crediarios():
    """Lista todos os crediários para o usuário logado."""
    crediarios = Crediario.get_all_for_user(current_user.id)
    return render_template('crediarios/list.html', crediarios=crediarios)


@crediario_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_crediario():
    """Adiciona um novo crediário."""
    # Obtém os tipos de crediário cadastrados pelo usuário logado
    tipos_crediario_disponiveis = TipoCrediario.get_all_for_user(
        current_user.id)

    if request.method == 'POST':
        crediario_nome = request.form['crediario']
        # Este será o nome do tipo (string)
        tipo_selecionado = request.form['tipo']
        final = request.form['final']
        limite = request.form['limite']

        if not (crediario_nome and tipo_selecionado and final and limite):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template('crediarios/add.html', tipos_crediario=tipos_crediario_disponiveis)

        try:
            limite_float = float(limite)
            final_int = int(final)

            # O campo 'tipo' no modelo Crediario ainda é uma string
            new_crediario = Crediario.add(
                crediario_nome, tipo_selecionado, final_int, limite_float, current_user.id
            )
            if new_crediario:
                flash('Crediário adicionado com sucesso!', 'success')
                return redirect(url_for('crediarios.list_crediarios'))
            else:
                flash(
                    'Não foi possível adicionar o crediário. Verifique os logs do servidor.', 'danger')
        except UniqueViolation:
            flash(
                f"Erro: Já existe um crediário com este nome e final para este usuário.", 'danger')
        except ValueError as e:
            flash(f'Erro de valor: {e}', 'warning')
        except Exception as e:
            print(f"Erro inesperado ao adicionar crediário: {e}")
            flash('Ocorreu um erro inesperado ao adicionar o crediário.', 'danger')

    return render_template('crediarios/add.html', tipos_crediario=tipos_crediario_disponiveis)


@crediario_bp.route('/edit/<int:crediario_id>', methods=['GET', 'POST'])
@login_required
def edit_crediario(crediario_id):
    """Edita um crediário existente."""
    crediario = Crediario.get_by_id(crediario_id, current_user.id)
    if not crediario:
        flash('Crediário não encontrado ou você não tem permissão para editá-lo.', 'danger')
        return redirect(url_for('crediarios.list_crediarios'))

    # Obtém os tipos de crediário cadastrados pelo usuário logado
    tipos_crediario_disponiveis = TipoCrediario.get_all_for_user(
        current_user.id)

    if request.method == 'POST':
        crediario_nome = request.form['crediario']
        # Este será o nome do tipo (string)
        tipo_selecionado = request.form['tipo']
        final = request.form['final']
        limite = request.form['limite']

        if not (crediario_nome and tipo_selecionado and final and limite):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template('crediarios/edit.html', crediario=crediario, tipos_crediario=tipos_crediario_disponiveis)

        try:
            limite_float = float(limite)
            final_int = int(final)

            # O campo 'tipo' no modelo Crediario ainda é uma string
            updated_crediario = Crediario.update(
                crediario_id, crediario_nome, tipo_selecionado, final_int, limite_float, current_user.id
            )
            if updated_crediario:
                flash('Crediário atualizado com sucesso!', 'success')
                return redirect(url_for('crediarios.list_crediarios'))
            else:
                flash(
                    'Não foi possível atualizar o crediário. Verifique os logs do servidor.', 'danger')
        except UniqueViolation:
            flash(
                f"Erro: Já existe outro crediário com este nome e final para este usuário.", 'danger')
        except ValueError as e:
            flash(f'Erro de valor: {e}', 'warning')
        except Exception as e:
            print(f"Erro inesperado ao atualizar crediário: {e}")
            flash('Ocorreu um erro inesperado ao atualizar o crediário.', 'danger')

    return render_template('crediarios/edit.html', crediario=crediario, tipos_crediario=tipos_crediario_disponiveis)


@crediario_bp.route('/delete/<int:crediario_id>', methods=['POST'])
@login_required
def delete_crediario(crediario_id):
    """Exclui um crediário."""
    crediario = Crediario.get_by_id(crediario_id, current_user.id)
    if not crediario:
        flash(
            'Crediário não encontrado ou você não tem permissão para excluí-lo.', 'danger')
        return redirect(url_for('crediarios.list_crediarios'))

    try:
        if Crediario.delete(crediario_id, current_user.id):
            flash(
                f'Crediário "{crediario.crediario}" excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir crediário.', 'danger')
    except Exception as e:
        print(f"Erro inesperado ao excluir crediário: {e}")
        flash('Ocorreu um erro inesperado ao excluir o crediário.', 'danger')

    return redirect(url_for('crediarios.list_crediarios'))
