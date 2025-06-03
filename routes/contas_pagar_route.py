from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.contas_pagar_model import ContasPagar
from flask_login import login_required, current_user  # Importa current_user

contas_pagar_bp = Blueprint(
    'contas_pagar', __name__, url_prefix='/contas_pagar')

# Renomeado para evitar conflito e clareza
TIPOS_CONTA_PAGAR = ["Receita", "Despesa"]


@contas_pagar_bp.route('/')
@login_required
def list_contas_pagar():
    # Busca apenas as contas a pagar do usuário logado
    contas_pagar = ContasPagar.get_all_for_user(current_user.id)
    return render_template('contas_pagar/list.html', contas_pagar=contas_pagar)


@contas_pagar_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_contas_pagar():
    if request.method == 'POST':
        conta = request.form['conta']
        tipo = request.form['tipo']

        if not (conta and tipo):
            flash('Conta e Tipo são obrigatórios!', 'warning')
            # Passa para o template
            return render_template('contas_pagar/add.html', tipos_conta_pagar=TIPOS_CONTA_PAGAR)

        # Validação do tipo (já está no modelo, mas bom ter aqui também)
        if tipo not in TIPOS_CONTA_PAGAR:
            flash("Tipo de conta inválido. Deve ser 'Receita' ou 'Despesa'.", 'warning')
            return render_template('contas_pagar/add.html', tipos_conta_pagar=TIPOS_CONTA_PAGAR)

        try:
            # Adiciona a conta a pagar para o usuário logado
            if ContasPagar.add(conta, tipo, current_user.id):
                flash('Conta adicionada com sucesso!', 'success')
                return redirect(url_for('contas_pagar.list_contas_pagar'))
            else:
                flash(
                    'Erro ao adicionar conta. Verifique os logs do servidor.', 'danger')
        except ValueError as e:  # Captura a exceção de UniqueViolation do modelo
            flash(f'Erro: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao adicionar conta a pagar: {e}")
            flash('Ocorreu um erro inesperado ao adicionar a conta.', 'danger')

    return render_template('contas_pagar/add.html', tipos_conta_pagar=TIPOS_CONTA_PAGAR)


@contas_pagar_bp.route('/edit/<int:conta_id>', methods=['GET', 'POST'])
@login_required
def edit_conta_pagar(conta_id):  # Renomeado de edit_user para edit_conta_pagar
    # Busca a conta a pagar pelo ID e pelo user_id para garantir que o usuário só edite as suas
    conta_pagar = ContasPagar.get_by_id(
        conta_id, current_user.id)  
    if not conta_pagar:
        flash('Conta não encontrada ou você não tem permissão para editá-la.', 'danger')
        return redirect(url_for('contas_pagar.list_contas_pagar'))

    if request.method == 'POST':
        conta = request.form['conta']
        tipo = request.form['tipo']

        if not (conta and tipo):
            flash('Conta e Tipo são obrigatórios!', 'warning')
            # Passa para o template
            return render_template('contas_pagar/edit.html', conta_pagar=conta_pagar, tipos_conta_pagar=TIPOS_CONTA_PAGAR)

        # Validação do tipo (já está no modelo, mas bom ter aqui também)
        if tipo not in TIPOS_CONTA_PAGAR:
            flash("Tipo de conta inválido. Deve ser 'Receita' ou 'Despesa'.", 'warning')
            return render_template('contas_pagar/edit.html', conta_pagar=conta_pagar, tipos_conta_pagar=TIPOS_CONTA_PAGAR)

        try:
            # Atualiza a conta a pagar, passando o user_id para a validação
            if ContasPagar.update(conta_id, conta, tipo, current_user.id):  # Passa user_id
                flash('Conta atualizada com sucesso!', 'success')
                return redirect(url_for('contas_pagar.list_contas_pagar'))
            else:
                flash(
                    'Erro ao atualizar conta. Verifique os logs do servidor.', 'danger')
        except ValueError as e:  # Captura a exceção de UniqueViolation do modelo
            flash(f'Erro: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao atualizar conta a pagar: {e}")
            flash('Ocorreu um erro inesperado ao atualizar a conta.', 'danger')

    # Passa conta_pagar e tipos_conta_pagar
    return render_template('contas_pagar/edit.html', conta_pagar=conta_pagar, tipos_conta_pagar=TIPOS_CONTA_PAGAR)


@contas_pagar_bp.route('/delete/<int:conta_id>', methods=['POST'])
@login_required
# Renomeado de delete_conta para delete_conta_pagar
def delete_conta_pagar(conta_id):
    # Busca a conta a pagar pelo ID e pelo user_id para garantir que o usuário só exclua as suas
    conta_pagar = ContasPagar.get_by_id(conta_id, current_user.id)
    if not conta_pagar:
        flash('Conta não encontrada ou você não tem permissão para excluí-la.', 'danger')
        return redirect(url_for('contas_pagar.list_contas_pagar'))

    # Exclui a conta a pagar, passando o user_id para a validação
    if ContasPagar.delete(conta_id, current_user.id):
        flash('Conta excluída com sucesso!', 'success')
    else:
        flash('Erro ao excluir conta.', 'danger')
    return redirect(url_for('contas_pagar.list_contas_pagar'))
