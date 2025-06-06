# routes/extrato_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import calendar  # Necessário para funções de calendário, se utilizadas no futuro ou na rota

# Importe os modelos necessários
from models.conta_bancaria_model import ContaBancaria
from models.movimento_bancario_model import MovimentoBancario
# Necessário para verificar a senha do usuário na exclusão
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

    # Tenta obter os parâmetros do POST (se for submissão de formulário)
    conta_id = request.form.get('conta_id')
    mes_ano_str = request.form.get('mes_ano')

    # Se não vierem do POST, tenta obter do GET (se for redirecionamento, como após a exclusão)
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
        'extrato/extrato_bancario.html',  # <--- Caminho do template atualizado
        title='Extrato Bancário',
        contas=contas,
        movimentos=movimentos,
        conta_selecionada=conta_selecionada,
        saldo_inicial_mes=saldo_inicial_mes,
        saldo_final_mes=saldo_final_mes,
        meses_disponiveis=meses_disponiveis,
        mes_extrato=mes_extrato,
        ano_extrato=ano_extrato,
        calendar=calendar  # Passando calendar caso ainda seja usado no template, embora não pareça
    )


@extrato_bp.route('/delete/<int:movimento_id>', methods=['POST'])
@login_required
def delete_movimento(movimento_id):
    # O usuário logado para verificar a senha
    user = current_user
    password = request.form.get('password')  # Pega a senha do formulário

    if not password:
        flash('Por favor, digite sua senha para confirmar a exclusão.', 'warning')
        # Redireciona de volta para o extrato, mantendo os filtros
        return redirect(url_for('extrato.extrato_bancario',  # <--- Rota de redirecionamento atualizada
                                conta_id=request.form.get('conta_id'),
                                mes_ano=request.form.get('mes_ano')))

    # Verifica a senha do usuário
    if not user.check_password(password):
        flash('Senha incorreta. A exclusão não foi realizada.', 'danger')
        return redirect(url_for('extrato.extrato_bancario',  # <--- Rota de redirecionamento atualizada
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
    return redirect(url_for('extrato.extrato_bancario',  # <--- Rota de redirecionamento atualizada
                            conta_id=request.form.get('conta_id'),
                            mes_ano=request.form.get('mes_ano')))
