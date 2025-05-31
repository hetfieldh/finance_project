
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import calendar

# Importe os modelos necessários
from models.conta_bancaria_model import ContaBancaria
from models.movimento_bancario_model import MovimentoBancario

movimento_bp = Blueprint('movimento', __name__, url_prefix='/movimento')


@movimento_bp.route('/')
@login_required
def index():
    return render_template('movimento/index.html', title='Visão Geral do Movimento')


@movimento_bp.route('/lancamento', methods=['GET', 'POST'])
@login_required
def mov_lancamento():
    contas = ContaBancaria.get_all_for_user(
        current_user.id)

    if request.method == 'POST':
        conta_id = request.form['conta_id']
        data_str = request.form['data']
        valor_str = request.form['valor']
        descricao = request.form['descricao']

        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            valor = float(valor_str.replace(',', '.'))

            MovimentoBancario.add(conta_id, data, valor, descricao)
            flash('Lançamento realizado com sucesso!', 'success')
            return redirect(url_for('movimento.mov_lancamento'))
        except ValueError as e:
            flash(f'Erro no lançamento: {e}', 'danger')
        except Exception as e:
            flash(f'Ocorreu um erro inesperado: {e}', 'danger')

    return render_template('movimento/lancamento.html', title='Novo Lançamento Bancário', contas=contas)


@movimento_bp.route('/resumo_contas')
@login_required
def mov_resumo_contas():
    contas = ContaBancaria.get_all_for_user(
        current_user.id)
    return render_template('movimento/resumo_bancario.html', title='Resumo Bancário', contas=contas)


@movimento_bp.route('/extrato', methods=['GET', 'POST'])
@login_required
def mov_extrato():
    contas = ContaBancaria.get_all_for_user(
        current_user.id)
    movimentos = []
    conta_selecionada = None
    saldo_inicial_mes = 0.0
    saldo_final_mes = 0.0
    mes_extrato = None
    ano_extrato = None

    if request.method == 'POST':
        conta_id = request.form.get('conta_id')
        mes_ano_str = request.form.get('mes_ano')

        if conta_id and mes_ano_str:
            try:
                conta_selecionada = ContaBancaria.get_by_id(
                    conta_id)  # <-- CLASSE RENOMEADA
                ano_extrato, mes_extrato = map(int, mes_ano_str.split('-'))

                movimentos = MovimentoBancario.get_extrato_mensal(
                    conta_id, ano_extrato, mes_extrato)

                saldo_inicial_mes = MovimentoBancario.get_saldo_inicial_do_mes(
                    conta_id, ano_extrato, mes_extrato)

                saldo_final_mes = saldo_inicial_mes + \
                    sum(m.valor for m in movimentos)

            except Exception as e:
                flash(f'Erro ao gerar extrato: {e}', 'danger')
        else:
            flash(
                'Por favor, selecione uma conta e um mês/ano para o extrato.', 'warning')

    meses_disponiveis = []
    today = datetime.now()
    for i in range(6):
        mes = today.month - i
        ano = today.year
        if mes <= 0:
            mes += 12
            ano -= 1
        meses_disponiveis.append({
            'value': f'{ano}-{mes:02d}',
            'label': f'{calendar.month_name[mes].capitalize()} de {ano}'
        })
    meses_disponiveis.reverse()

    return render_template(
        'movimento/extrato_bancario.html',
        title='Extrato Bancário',
        contas=contas,
        movimentos=movimentos,
        conta_selecionada=conta_selecionada,
        saldo_inicial_mes=saldo_inicial_mes,
        saldo_final_mes=saldo_final_mes,
        meses_disponiveis=meses_disponiveis,
        mes_extrato=mes_extrato,
        ano_extrato=ano_extrato
    )
