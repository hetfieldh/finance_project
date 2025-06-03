from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import calendar

# Importe os modelos necessários
from models.conta_bancaria_model import ContaBancaria
from models.movimento_bancario_model import MovimentoBancario
from models.transacao_model import Transacao
from models.user_model import User


movimento_bp = Blueprint('movimento', __name__, url_prefix='/movimento')


@movimento_bp.route('/')
@login_required
def index():
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


@movimento_bp.route('/extrato', methods=['GET', 'POST'])
@login_required
def mov_extrato():
    contas = ContaBancaria.get_all_for_user(current_user.id)
    movimentos = []
    conta_selecionada = None
    saldo_inicial_mes = 0.0
    saldo_final_mes = 0.0
    mes_extrato = None
    ano_extrato = None

    # Tenta obter os parâmetros do POST (se for submissão de formulário)
    conta_id = request.form.get('conta_id')
    mes_ano_str = request.form.get('mes_ano')

    # Se não vierem do POST, tenta obter do GET (se for redirecionamento)
    if not conta_id and not mes_ano_str:
        conta_id = request.args.get('conta_id')
        mes_ano_str = request.args.get('mes_ano')

    if conta_id and mes_ano_str:
        try:
            conta_selecionada = ContaBancaria.get_by_id(conta_id)
            if not conta_selecionada or conta_selecionada.user_id != current_user.id:
                flash(
                    'Conta bancária não encontrada ou não pertence ao usuário.', 'danger')
                # Limpa os parâmetros para não tentar carregar extrato inválido
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
            # Limpa os parâmetros em caso de erro para evitar loops ou exibição incorreta
            conta_id = None
            mes_ano_str = None
    elif request.method == 'POST':  # Se for POST e faltar parâmetros, exibe aviso
        flash('Por favor, selecione uma conta e um mês/ano para o extrato.', 'warning')

    # Dicionário com nomes dos meses em português
    meses_pt_br = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    # Gerar lista de meses disponíveis (mês atual e os 5 anteriores)
    meses_disponiveis = []
    today = datetime.now()
    for i in range(6):  # Loop para 6 meses (0 a 5)
        target_month = today.month - i
        target_year = today.year
        if target_month <= 0:  # Se o mês for menor ou igual a zero, ajusta para o ano anterior
            target_month += 12
            target_year -= 1

        meses_disponiveis.append({
            'value': f'{target_year}-{target_month:02d}',
            'label': f'{meses_pt_br[target_month]} de {target_year}'
        })
    meses_disponiveis.reverse()  # Para exibir os meses do mais antigo para o mais recente

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
        ano_extrato=ano_extrato,
        calendar=calendar
    )


@movimento_bp.route('/delete/<int:movimento_id>', methods=['POST'])
@login_required
def delete_movimento(movimento_id):
    # O usuário logado para verificar a senha
    user = current_user
    password = request.form.get('password')  # Pega a senha do formulário

    if not password:
        flash('Por favor, digite sua senha para confirmar a exclusão.', 'warning')
        # Redireciona de volta para o extrato, talvez mantendo os filtros
        return redirect(url_for('movimento.mov_extrato',
                                conta_id=request.form.get('conta_id'),
                                mes_ano=request.form.get('mes_ano')))

    # Verifica a senha do usuário
    if not user.check_password(password):
        flash('Senha incorreta. A exclusão não foi realizada.', 'danger')
        return redirect(url_for('movimento.mov_extrato',
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

    # Redireciona de volta para o extrato, idealmente mantendo os filtros de busca
    return redirect(url_for('movimento.mov_extrato',
                            conta_id=request.form.get('conta_id'),
                            mes_ano=request.form.get('mes_ano')))
