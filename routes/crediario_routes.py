# routes/crediario_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.crediario_model import Crediario
from flask_login import login_required, current_user  # Importa current_user
from datetime import datetime

crediario_bp = Blueprint('crediarios', __name__, url_prefix='/crediarios')

STATUS_CREDIARIO = ["Ativo", "Pago", "Atrasado"]


@crediario_bp.route('/')
@login_required
def list_crediarios():
    # Busca apenas os crediários do usuário logado
    crediarios = Crediario.get_all_for_user(current_user.id)
    return render_template('crediarios/list.html', crediarios=crediarios)


@crediario_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_crediario():
    if request.method == 'POST':
        # Os nomes dos campos foram ajustados para corresponder ao modelo Crediario atualizado
        nome_credor = request.form['nome_credor']
        valor_total = request.form['valor_total']
        parcelas = request.form['parcelas']
        valor_parcela = request.form['valor_parcela']
        data_vencimento_primeira_str = request.form['data_vencimento_primeira']
        status = request.form.get('status', 'Ativo')

        if not (nome_credor and valor_total and parcelas and valor_parcela and data_vencimento_primeira_str):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'warning')
            return render_template('crediarios/add.html', status_crediario=STATUS_CREDIARIO)

        try:
            valor_total_float = float(valor_total)
            parcelas_int = int(parcelas)
            valor_parcela_float = float(valor_parcela)
            data_vencimento_primeira = datetime.strptime(
                data_vencimento_primeira_str, '%Y-%m-%d').date()

            new_crediario = Crediario.add(
                # Passa o user_id do usuário logado
                current_user.id,
                nome_credor, valor_total_float, parcelas_int, valor_parcela_float,
                data_vencimento_primeira, status
            )
            if new_crediario:
                flash('Crediário adicionado com sucesso!', 'success')
                return redirect(url_for('crediarios.list_crediarios'))
            else:
                flash(
                    'Não foi possível adicionar o crediário. Verifique os logs do servidor.', 'danger')
        except ValueError as e:
            flash(f'Erro de valor: {e}', 'warning')
        except Exception as e:
            print(f"Erro inesperado ao adicionar crediário: {e}")
            flash('Ocorreu um erro inesperado ao adicionar o crediário.', 'danger')

    return render_template('crediarios/add.html', status_crediario=STATUS_CREDIARIO)


@crediario_bp.route('/edit/<int:crediario_id>', methods=['GET', 'POST'])
@login_required
def edit_crediario(crediario_id):
    # Busca o crediário pelo ID e pelo user_id para garantir que o usuário só edite os seus
    crediario = Crediario.get_by_id(crediario_id, current_user.id)
    if not crediario:
        flash('Crediário não encontrado ou você não tem permissão para editá-lo.', 'danger')
        return redirect(url_for('crediarios.list_crediarios'))

    if request.method == 'POST':
        # Os nomes dos campos foram ajustados para corresponder ao modelo Crediario atualizado
        nome_credor = request.form['nome_credor']
        valor_total = request.form['valor_total']
        parcelas = request.form['parcelas']
        valor_parcela = request.form['valor_parcela']
        data_vencimento_primeira_str = request.form['data_vencimento_primeira']
        status = request.form['status']

        if not (nome_credor and valor_total and parcelas and valor_parcela and data_vencimento_primeira_str and status):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'warning')
            return render_template('crediarios/edit.html', crediario=crediario, status_crediario=STATUS_CREDIARIO)

        try:
            valor_total_float = float(valor_total)
            parcelas_int = int(parcelas)
            valor_parcela_float = float(valor_parcela)
            data_vencimento_primeira = datetime.strptime(
                data_vencimento_primeira_str, '%Y-%m-%d').date()

            updated_crediario = Crediario.update(
                crediario_id, nome_credor, valor_total_float, parcelas_int, valor_parcela_float,
                # Passa o user_id para a validação
                data_vencimento_primeira, status, current_user.id
            )
            if updated_crediario:
                flash('Crediário atualizado com sucesso!', 'success')
                return redirect(url_for('crediarios.list_crediarios'))
            else:
                flash(
                    'Não foi possível atualizar o crediário. Verifique os logs do servidor.', 'danger')
        except ValueError as e:
            flash(f'Erro de valor: {e}', 'warning')
        except Exception as e:
            print(f"Erro inesperado ao atualizar crediário: {e}")
            flash('Ocorreu um erro inesperado ao atualizar o crediário.', 'danger')

    return render_template('crediarios/edit.html', crediario=crediario, status_crediario=STATUS_CREDIARIO)


@crediario_bp.route('/delete/<int:crediario_id>', methods=['POST'])
@login_required
def delete_crediario(crediario_id):
    # Busca o crediário pelo ID e pelo user_id para garantir que o usuário só exclua os seus
    crediario = Crediario.get_by_id(crediario_id, current_user.id)
    if not crediario:
        flash(
            'Crediário não encontrado ou você não tem permissão para excluí-lo.', 'danger')
        return redirect(url_for('crediarios.list_crediarios'))

    # Exclui o crediário, passando o user_id para a validação
    if Crediario.delete(crediario_id, current_user.id):
        flash('Crediário excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir crediário.', 'danger')
    return redirect(url_for('crediarios.list_crediarios'))
