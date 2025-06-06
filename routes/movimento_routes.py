# routes/movimento_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from models.conta_bancaria_model import ContaBancaria
from models.movimento_bancario_model import MovimentoBancario
from models.transacao_model import Transacao

movimento_bp = Blueprint('movimento', __name__, url_prefix='/movimento')


@movimento_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@movimento_bp.route('/lancamento', methods=['GET', 'POST'])
@login_required
def mov_lancamento():
    contas = ContaBancaria.get_all_for_user(current_user.id)
    transacoes = Transacao.get_all_for_user(current_user.id)

    contas_json_serializable = []
    for conta in contas:
        contas_json_serializable.append({
            'id': conta.id,
            'nome_banco': conta.nome_banco,
            'numero_conta': conta.numero_conta,
            'tipo_conta': conta.tipo_conta,
            'saldo_atual': float(conta.saldo_atual),
            'limite_credito': float(conta.limite_credito) if conta.limite_credito is not None else None
        })

    if request.method == 'POST':
        conta_id_origem = request.form['conta_id']
        data_str = request.form['data']
        valor_str = request.form['valor']
        descricao = request.form['descricao']
        is_transfer = 'is_transfer' in request.form
        conta_destino_id = request.form.get('conta_destino_id')

        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            valor = float(valor_str.replace(',', '.'))

            if is_transfer:
                if not conta_destino_id:
                    raise ValueError(
                        "Selecione a conta destino para a transferência.")
                if str(conta_id_origem) == str(conta_destino_id):
                    raise ValueError(
                        "Conta de origem e conta de destino não podem ser a mesma.")

                descricao_transferencia = "Transferência entre contas"

                MovimentoBancario.transfer(
                    conta_id_origem,
                    conta_destino_id,
                    abs(valor),
                    descricao_transferencia
                )
                flash('Transferência realizada com sucesso!', 'success')
            else:
                MovimentoBancario.add(conta_id_origem, data, valor, descricao)
                flash('Lançamento realizado com sucesso!', 'success')

            return redirect(url_for('movimento.mov_lancamento'))

        except ValueError as e:
            flash(f'Erro no lançamento: {e}', 'danger')
        except Exception as e:
            flash(f'Ocorreu um erro inesperado: {e}', 'danger')

    return render_template('movimento/lancamento.html', title='Novo Lançamento Bancário', contas=contas_json_serializable, transacoes=transacoes)


@movimento_bp.route('/resumo_contas')
@login_required
def mov_resumo_contas():
    contas = ContaBancaria.get_all_for_user(current_user.id)
    return render_template('movimento/resumo_bancario.html', title='Resumo Bancário', contas=contas)
