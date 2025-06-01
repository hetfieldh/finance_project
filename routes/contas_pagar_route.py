from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.contas_pagar_model import ContasPagar
from flask_login import login_required

contas_pagar_bp = Blueprint(
    'contas_pagar', __name__, url_prefix='/contas_pagar')


@contas_pagar_bp.route('/')
@login_required
def list_contas_pagar():
    contas_pagar = ContasPagar.get_all()
    return render_template('contas_pagar/list.html', contas_pagar=contas_pagar)


@contas_pagar_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_contas_pagar():
    if request.method == 'POST':
        conta = request.form['conta']
        tipo = request.form['tipo']
        if conta and tipo:
            if ContasPagar.add(conta, tipo):
                flash('Conta adicionada com sucesso!', 'success')
                return redirect(url_for('contas_pagar.list_contas_pagar'))
            else:
                flash(
                    'Erro ao adicionar conta. Esta conta pode já existir ou o tipo está incorreto.', 'danger')
        else:
            flash('Conta e Tipo são obrigatórios!', 'warning')
    return render_template('contas_pagar/add.html')


@contas_pagar_bp.route('/edit/<int:conta_id>', methods=['GET', 'POST'])
@login_required
def edit_user(conta_id):
    user = ContasPagar.get_by_id(conta_id)
    if not user:
        flash('Conta não encontrada.', 'danger')
        return redirect(url_for('contas_pagar.list_contas_pagar'))

    if request.method == 'POST':
        conta = request.form['conta']
        tipo = request.form['tipo']
        if conta and tipo:
            if ContasPagar.update(conta_id, conta, tipo):
                flash('Conta atualizada com sucesso!', 'success')
                return redirect(url_for('contas_pagar.list_contas_pagar'))
            else:
                flash('Erro ao atualizar conta. Verifique o tipo.', 'danger')
        else:
            flash('Conta e Tipo são obrigatórios!', 'warning')

    return render_template('contas_pagar/edit.html', conta=user)


@contas_pagar_bp.route('/delete/<int:conta_id>', methods=['POST'])
@login_required
def delete_conta(conta_id):
    if ContasPagar.delete(conta_id):
        flash('Conta excluída com sucesso!', 'success')
    else:
        flash('Erro ao excluir conta.', 'danger')
    return redirect(url_for('contas_pagar.list_contas_pagar'))
