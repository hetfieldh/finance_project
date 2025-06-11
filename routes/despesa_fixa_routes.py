# routes/despesa_fixa_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date
from models.despesa_fixa_model import DespesaFixa
from models.contas_pagar_model import ContasPagar

despesas_fixas_bp = Blueprint(
    'despesa_fixa', __name__, url_prefix='/despesa_fixa')


@despesas_fixas_bp.route('/')
@login_required
def list_despesas_fixas():
    despesas_fixas = DespesaFixa.get_all_for_user(current_user.id)
    return render_template('despesas_fixas/list.html', despesas_fixas=despesas_fixas)


@despesas_fixas_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_despesa_fixa():
    # Filtrar contas a pagar para mostrar apenas as do tipo 'Despesa'
    todas_contas = ContasPagar.get_all_for_user(current_user.id)
    contas_despesa = [c for c in todas_contas if c.tipo == 'Despesa']

    if request.method == 'POST':
        conta_pagar_id = request.form['conta_pagar_id']
        mes_ano_str = request.form['mes_ano']
        valor_str = request.form['valor']

        if not (conta_pagar_id and mes_ano_str and valor_str):
            flash(
                'Todos os campos (Despesa Fixa, Mês/Ano e Valor) são obrigatórios!', 'warning')
            current_month = datetime.now().strftime('%Y-%m')
            return render_template('despesas_fixas/add.html', current_month_str=current_month, contas_pagar=contas_despesa)

        try:
            conta_selecionada = ContasPagar.get_by_id(
                conta_pagar_id, current_user.id)
            if not conta_selecionada or conta_selecionada.tipo != 'Despesa':
                flash('Conta de despesa selecionada inválida.', 'danger')
                current_month = datetime.now().strftime('%Y-%m')
                return render_template('despesas_fixas/add.html', current_month_str=current_month, contas_pagar=contas_despesa)

            descricao = conta_selecionada.conta

            mes_ano = datetime.strptime(mes_ano_str, '%Y-%m').date()
            valor = float(valor_str)

            if DespesaFixa.add(current_user.id, descricao, mes_ano, valor):
                flash('Despesa fixa cadastrada com sucesso!', 'success')
                return redirect(url_for('despesa_fixa.add_despesa_fixa'))
            else:
                flash(
                    'Erro ao adicionar despesa fixa. Verifique os logs do servidor.', 'danger')
        except ValueError as e:
            flash(
                f'Erro no formato dos dados: {e}. Certifique-se de que o valor é um número válido e a data está correta.', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao adicionar despesa fixa: {e}")
            flash('Ocorreu um erro inesperado ao adicionar a despesa fixa.', 'danger')

    current_month = datetime.now().strftime('%Y-%m')
    return render_template('despesas_fixas/add.html', current_month_str=current_month, contas_pagar=contas_despesa)


@despesas_fixas_bp.route('/edit/<int:despesa_id>', methods=['GET', 'POST'])
@login_required
def edit_despesa_fixa(despesa_id):
    despesa = DespesaFixa.get_by_id(despesa_id, current_user.id)
    if not despesa:
        flash(
            'Despesa fixa não encontrada ou você não tem permissão para editá-la.', 'danger')
        return redirect(url_for('despesa_fixa.list_despesas_fixas'))

    # Filtrar contas a pagar para mostrar apenas as do tipo 'Despesa'
    todas_contas = ContasPagar.get_all_for_user(current_user.id)
    contas_despesa = [c for c in todas_contas if c.tipo == 'Despesa']

    if request.method == 'POST':
        conta_pagar_id = request.form['conta_pagar_id']
        mes_ano_str = request.form['mes_ano']
        valor_str = request.form['valor']

        if not (conta_pagar_id and mes_ano_str and valor_str):
            flash(
                'Todos os campos (Despesa Fixa, Mês/Ano e Valor) são obrigatórios!', 'warning')
            return render_template('despesas_fixas/edit.html', despesa=despesa, contas_pagar=contas_despesa)

        try:
            conta_selecionada = ContasPagar.get_by_id(
                conta_pagar_id, current_user.id)
            if not conta_selecionada or conta_selecionada.tipo != 'Despesa':
                flash('Conta de despesa selecionada inválida.', 'danger')
                return render_template('despesas_fixas/edit.html', despesa=despesa, contas_pagar=contas_despesa)

            descricao = conta_selecionada.conta

            mes_ano = datetime.strptime(mes_ano_str, '%Y-%m').date()
            valor = float(valor_str)

            if DespesaFixa.update(despesa_id, current_user.id, descricao, mes_ano, valor):
                flash('Despesa fixa atualizada com sucesso!', 'success')
                return redirect(url_for('despesa_fixa.list_despesas_fixas'))
            else:
                flash(
                    'Erro ao atualizar despesa fixa. Verifique os logs do servidor.', 'danger')
        except ValueError as e:
            flash(
                f'Erro no formato dos dados: {e}. Verifique os valores.', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao atualizar despesa fixa: {e}")
            flash('Ocorreu um erro inesperado ao atualizar a despesa fixa.', 'danger')

    return render_template('despesas_fixas/edit.html', despesa=despesa, contas_pagar=contas_despesa)


@despesas_fixas_bp.route('/delete/<int:despesa_id>', methods=['POST'])
@login_required
def delete_despesa_fixa(despesa_id):
    despesa = DespesaFixa.get_by_id(despesa_id, current_user.id)
    if not despesa:
        flash('Despesa fixa não encontrada ou você não tem permissão para excluí-la.', 'danger')
        return redirect(url_for('despesa_fixa.list_despesas_fixas'))

    try:
        if DespesaFixa.delete(despesa_id, current_user.id):
            flash('Despesa fixa excluída com sucesso!', 'success')
        else:
            flash('Erro ao excluir despesa fixa.', 'danger')
    except Exception as e:
        print(f"Erro inesperado ao excluir despesa fixa: {e}")
        flash('Ocorreu um erro inesperado ao excluir a despesa fixa.', 'danger')
    return redirect(url_for('despesa_fixa.list_despesas_fixas'))
