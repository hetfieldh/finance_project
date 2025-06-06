# routes/extrato_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import calendar

from models.conta_bancaria_model import ContaBancaria
from models.movimento_bancario_model import MovimentoBancario
from models.user_model import User


extrato_bp = Blueprint('extrato', __name__, url_prefix='/extratos')


@extrato_bp.route('/bancario', methods=['GET', 'POST'])
@login_required
def extrato_bancario():
    contas = ContaBancaria.get_all_for_user(current_user.id)
    movimentos = []
    conta_selecionada = None
    saldo_inicial_mes = 0.0
    saldo_final_mes = 0.0
    mes_extrato = None
    ano_extrato = None

    conta_id = request.form.get('conta_id')
    mes_ano_str = request.form.get('mes_ano')

    if not conta_id and not mes_ano_str:
        conta_id = request.args.get('conta_id')
        mes_ano_str = request.args.get('mes_ano')

    if conta_id and mes_ano_str:
        try:
            conta_selecionada = ContaBancaria.get_by_id(conta_id)
            if not conta_selecionada or conta_selecionada.user_id != current_user.id:
                flash(
                    'Conta bancária não encontrada ou não pertence ao usuário.', 'danger')
                conta_id = None
                mes_ano_str = None
            else:
                ano_extrato, mes_extrato = map(int, mes_ano_str.split('-'))

                movimentos = MovimentoBancario.get_extrato_mensal(
                    conta_id, ano_extrato, mes_extrato)

                saldo_inicial_mes = MovimentoBancario.get_saldo_inicial_do_mes(
                    conta_id, ano_extrato, mes_extrato)

                saldo_final_mes = saldo_inicial_mes + \
                    sum(m.valor for m in movimentos)

        except Exception as e:
            flash(f'Erro ao gerar extrato: {e}', 'danger')
            conta_id = None
            mes_ano_str = None
    elif request.method == 'POST':
        flash('Por favor, selecione uma conta e um mês/ano para o extrato.', 'warning')

    meses_pt_br = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    meses_disponiveis = []
    today = datetime.now()
    for i in range(6):
        target_month = today.month - i
        target_year = today.year
        if target_month <= 0:
            target_month += 12
            target_year -= 1

        meses_disponiveis.append({
            'value': f'{target_year}-{target_month:02d}',
            'label': f'{meses_pt_br[target_month]} de {target_year}'
        })
    meses_disponiveis.reverse()

    return render_template(
        'extrato/extrato_bancario.html',
        title='Extrato Bancário',
        contas=contas,
        movimentos=movimentos,
        conta_selecionada=conta_selecionada,
        saldo_inicial_mes=saldo_inicial_mes,
        saldo_final_mes=saldo_final_mes,
        meses_disponiveis=meses_disponiveis,
        mes_extrato=mes_extrato,
        ano_extrato=ano_extrato,
        calendar=calendar
    )


@extrato_bp.route('/delete/<int:movimento_id>', methods=['POST'])
@login_required
def delete_movimento(movimento_id):
    user = current_user
    password = request.form.get('password')

    if not password:
        flash('Por favor, digite sua senha para confirmar a exclusão.', 'warning')
        return redirect(url_for('extrato.extrato_bancario',
                                conta_id=request.form.get('conta_id'),
                                mes_ano=request.form.get('mes_ano')))

    if not user.check_password(password):
        flash('Senha incorreta. A exclusão não foi realizada.', 'danger')
        return redirect(url_for('extrato.extrato_bancario',
                                conta_id=request.form.get('conta_id'),
                                mes_ano=request.form.get('mes_ano')))

    try:
        if MovimentoBancario.delete(movimento_id, user.id):
            flash('Lançamento excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir lançamento.', 'danger')
    except ValueError as e:
        flash(f'Erro ao excluir lançamento: {e}', 'danger')
    except Exception as e:
        flash(
            f'Ocorreu um erro inesperado ao excluir o lançamento: {e}', 'danger')

    return redirect(url_for('extrato.extrato_bancario',
                            conta_id=request.form.get('conta_id'),
                            mes_ano=request.form.get('mes_ano')))
