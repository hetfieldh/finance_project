from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.tipo_crediario_model import TipoCrediario
from flask_login import login_required, current_user


tipo_crediario_bp = Blueprint(
    'tipos_crediario', __name__, url_prefix='/tipos_crediario')


@tipo_crediario_bp.route('/')
@login_required
def list_tipos_crediario():
    """Lista todos os tipos de crediário para o usuário logado."""
    tipos = TipoCrediario.get_all_for_user(current_user.id)
    return render_template('tipos_crediario/list.html', tipos=tipos)


@tipo_crediario_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_tipo_crediario():
    """Adiciona um novo tipo de crediário."""
    if request.method == 'POST':
        nome_tipo = request.form['nome_tipo'].strip()
        # Captura o URL de onde a requisição veio, se disponível
        next_url = request.form.get('next_url') or url_for(
            'tipos_crediario.list_tipos_crediario')

        if not nome_tipo:
            flash('O nome do tipo de crediário é obrigatório!', 'warning')
            return render_template('tipos_crediario/add.html')

        try:
            TipoCrediario.add(current_user.id, nome_tipo)
            flash(
                f'Tipo de crediário "{nome_tipo}" adicionado com sucesso!', 'success')
            # Redireciona para o URL de onde veio, ou para a lista de tipos de crediário
            return redirect(next_url)
        except ValueError as e:
            flash(f'Erro ao adicionar tipo de crediário: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao adicionar tipo de crediário: {e}")
            flash(
                'Ocorreu um erro inesperado ao adicionar o tipo de crediário.', 'danger')

    return render_template('tipos_crediario/add.html', next_url=request.referrer)


@tipo_crediario_bp.route('/edit/<int:tipo_id>', methods=['GET', 'POST'])
@login_required
def edit_tipo_crediario(tipo_id):
    """Edita um tipo de crediário existente."""
    tipo = TipoCrediario.get_by_id(tipo_id, current_user.id)
    if not tipo:
        flash('Tipo de crediário não encontrado ou você não tem permissão para editá-lo.', 'danger')
        return redirect(url_for('tipos_crediario.list_tipos_crediario'))

    if request.method == 'POST':
        nome_tipo = request.form['nome_tipo'].strip()

        if not nome_tipo:
            flash('O nome do tipo de crediário é obrigatório!', 'warning')
            return render_template('tipos_crediario/edit.html', tipo=tipo)

        try:
            TipoCrediario.update(tipo_id, nome_tipo, current_user.id)
            flash(
                f'Tipo de crediário "{nome_tipo}" atualizado com sucesso!', 'success')
            return redirect(url_for('tipos_crediario.list_tipos_crediario'))
        except ValueError as e:
            flash(f'Erro ao atualizar tipo de crediário: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao atualizar tipo de crediário: {e}")
            flash(
                'Ocorreu um erro inesperado ao atualizar o tipo de crediário.', 'danger')

    return render_template('tipos_crediario/edit.html', tipo=tipo)


@tipo_crediario_bp.route('/delete/<int:tipo_id>', methods=['POST'])
@login_required
def delete_tipo_crediario(tipo_id):
    """Exclui um tipo de crediário."""
    tipo = TipoCrediario.get_by_id(tipo_id, current_user.id)
    if not tipo:
        flash('Tipo de crediário não encontrado ou você não tem permissão para excluí-lo.', 'danger')
        return redirect(url_for('tipos_crediario.list_tipos_crediario'))

    try:
        if TipoCrediario.delete(tipo_id, current_user.id):
            flash(
                f'Tipo de crediário "{tipo.nome_tipo}" excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir tipo de crediário.', 'danger')
    except Exception as e:
        print(f"Erro inesperado ao excluir tipo de crediário: {e}")
        flash('Ocorreu um erro inesperado ao excluir o tipo de crediário.', 'danger')

    return redirect(url_for('tipos_crediario.list_tipos_crediario'))
