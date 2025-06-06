# routes/movimento_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime  # timedelta e calendar não são mais necessários aqui
# import calendar # Não é mais necessário se não for usado em outras rotas de movimento

# Importe os modelos necessários
from models.conta_bancaria_model import ContaBancaria
from models.movimento_bancario_model import MovimentoBancario
from models.transacao_model import Transacao
# from models.user_model import User # Não é mais necessário aqui se user.check_password for só no extrato/exclusão


movimento_bp = Blueprint('movimento', __name__, url_prefix='/movimento')


@movimento_bp.route('/')
@login_required
def index():
    # Se você removeu templates/movimento/index.html, esta rota pode precisar de ajuste
    # ou ser removida se não for mais usada.
    # Por enquanto, vou manter, mas com a observação.
    return render_template('movimento/index.html', title='Visão Geral do Movimento')


@movimento_bp.route('/lancamento', methods=['GET', 'POST'])
@login_required
def mov_lancamento():
    contas = ContaBancaria.get_all_for_user(current_user.id)
    transacoes = Transacao.get_all_for_user(current_user.id)

    # CONVERTER OBJETOS ContaBancaria PARA DICIONÁRIOS JSON-SERIALIZÁVEIS
    contas_json_serializable = []
    for conta in contas:
        contas_json_serializable.append({
            'id': conta.id,
            'nome_banco': conta.nome_banco,
            'numero_conta': conta.numero_conta,
            'tipo_conta': conta.tipo_conta,
            # Garante que é float para JSON
            'saldo_atual': float(conta.saldo_atual),
            'limite_credito': float(conta.limite_credito) if conta.limite_credito is not None else None
        })

    if request.method == 'POST':
        conta_id_origem = request.form['conta_id']
        data_str = request.form['data']
        valor_str = request.form['valor']
        descricao = request.form['descricao']
        # Verifica se o checkbox foi marcado
        is_transfer = 'is_transfer' in request.form
        # Pode ser None se não for transferência
        conta_destino_id = request.form.get('conta_destino_id')

        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            valor = float(valor_str.replace(',', '.'))

            if is_transfer:
                if not conta_destino_id:
                    raise ValueError(
                        "Selecione a conta destino para a transferência.")
                # Comparar como string para evitar problemas de tipo
                if str(conta_id_origem) == str(conta_destino_id):
                    raise ValueError(
                        "Conta de origem e conta de destino não podem ser a mesma.")

                # Para transferência, o valor é sempre positivo no formulário,
                # mas será negativo na origem e positivo no destino.
                # A descrição pode ser padronizada para "Transferência"
                # Ou buscar um tipo de transação "Transferência"
                descricao_transferencia = "Transferência entre contas"

                # Chamar o novo método de transferência no modelo
                MovimentoBancario.transfer(
                    conta_id_origem,
                    conta_destino_id,
                    abs(valor),  # O valor da transferência é sempre positivo
                    descricao_transferencia
                )
                flash('Transferência realizada com sucesso!', 'success')
            else:
                # Lançamento normal (receita ou despesa)
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
