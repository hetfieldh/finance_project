# routes/movimento_crediario_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

# Importa os modelos necessários
from models.movimento_crediario_model import MovimentoCrediario
from models.grupo_crediario_model import GrupoCrediario
from models.crediario_model import Crediario

movimento_crediario_bp = Blueprint(
    'movimento_crediario', __name__, url_prefix='/movimento_crediario')


@movimento_crediario_bp.route('/')
@login_required
def list_movimentos_crediario():
    movimentos = MovimentoCrediario.get_all_for_user(current_user.id)
    return render_template('movimento_crediario/list.html', movimentos=movimentos)


@movimento_crediario_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_movimento_crediario():
    grupos_crediario = GrupoCrediario.get_all_for_user(current_user.id)
    crediarios_disponiveis = Crediario.get_all_for_user(current_user.id)

    today_date_str = date.today().isoformat()
    current_month_str = date.today().strftime('%Y-%m')

    if request.method == 'POST':
        data_compra_str = request.form['data_compra']
        descricao = request.form['descricao']
        id_grupo_crediario = request.form['id_grupo_crediario']
        id_crediario = request.form['id_crediario']
        valor_total_str = request.form['valor_total']
        num_parcelas_str = request.form['num_parcelas']
        primeira_parcela_str = request.form['primeira_parcela']

        if not all([data_compra_str, descricao, id_grupo_crediario, id_crediario,
                    valor_total_str, num_parcelas_str, primeira_parcela_str]):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template(
                'movimento_crediario/add.html',
                grupos_crediario=grupos_crediario,
                crediarios_disponiveis=crediarios_disponiveis,
                today_date_str=today_date_str,
                current_month_str=current_month_str
            )

        try:
            data_compra = date.fromisoformat(data_compra_str)
            primeira_parcela = date.fromisoformat(primeira_parcela_str + '-01')
            valor_total = float(valor_total_str)
            num_parcelas = int(num_parcelas_str)

            if valor_total <= 0 or num_parcelas <= 0:
                flash(
                    'Valor Total e Número de Parcelas devem ser maiores que zero.', 'warning')
                return render_template(
                    'movimento_crediario/add.html',
                    grupos_crediario=grupos_crediario,
                    crediarios_disponiveis=crediarios_disponiveis,
                    today_date_str=today_date_str,
                    current_month_str=current_month_str
                )

            MovimentoCrediario.add(
                data_compra, descricao, id_grupo_crediario, id_crediario,
                valor_total, num_parcelas, primeira_parcela, current_user.id
            )
            flash('Movimento de Crediário adicionado com sucesso!', 'success')
            return redirect(url_for('movimento_crediario.list_movimentos_crediario'))
        except ValueError as e:
            flash(f'Erro de validação: {e}', 'danger')
            return render_template(
                'movimento_crediario/add.html',
                grupos_crediario=grupos_crediario,
                crediarios_disponiveis=crediarios_disponiveis,
                today_date_str=today_date_str,
                current_month_str=current_month_str
            )
        except Exception as e:
            print(f"Erro inesperado ao adicionar movimento de crediário: {e}")
            flash('Ocorreu um erro inesperado ao adicionar o movimento.', 'danger')
            # Renderiza o formulário com os valores padrão e a mensagem de erro
            return render_template(
                'movimento_crediario/add.html',
                grupos_crediario=grupos_crediario,
                crediarios_disponiveis=crediarios_disponiveis,
                today_date_str=today_date_str,
                current_month_str=current_month_str
            )

    return render_template(
        'movimento_crediario/add.html',
        grupos_crediario=grupos_crediario,
        crediarios_disponiveis=crediarios_disponiveis,
        today_date_str=today_date_str,
        current_month_str=current_month_str
    )


@movimento_crediario_bp.route('/edit/<int:movimento_id>', methods=['GET', 'POST'])
@login_required
def edit_movimento_crediario(movimento_id):
    movimento = MovimentoCrediario.get_by_id(movimento_id, current_user.id)
    if not movimento:
        flash('Movimento de Crediário não encontrado ou você não tem permissão para editá-lo.', 'danger')
        return redirect(url_for('movimento_crediario.list_movimentos_crediario'))

    grupos_crediario = GrupoCrediario.get_all_for_user(current_user.id)
    crediarios_disponiveis = Crediario.get_all_for_user(current_user.id)

    # Obtenha a data atual formatada para o input type="date" e "month"
    today_date_str = date.today().isoformat()
    current_month_str = date.today().strftime('%Y-%m')

    if request.method == 'POST':
        data_compra_str = request.form['data_compra']
        descricao = request.form['descricao']
        id_grupo_crediario = request.form['id_grupo_crediario']
        id_crediario = request.form['id_crediario']
        valor_total_str = request.form['valor_total']
        num_parcelas_str = request.form['num_parcelas']
        primeira_parcela_str = request.form['primeira_parcela']

        if not all([data_compra_str, descricao, id_grupo_crediario, id_crediario,
                    valor_total_str, num_parcelas_str, primeira_parcela_str]):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template(
                'movimento_crediario/edit.html',
                movimento=movimento,
                grupos_crediario=grupos_crediario,
                crediarios_disponiveis=crediarios_disponiveis,
                today_date_str=today_date_str,
                current_month_str=current_month_str
            )
        try:
            data_compra = date.fromisoformat(data_compra_str)
            # Para primeira_parcela, assuma o dia 1 do mês selecionado
            primeira_parcela = date.fromisoformat(primeira_parcela_str + '-01')
            valor_total = float(valor_total_str)
            num_parcelas = int(num_parcelas_str)

            if valor_total <= 0 or num_parcelas <= 0:
                flash(
                    'Valor Total e Número de Parcelas devem ser maiores que zero.', 'warning')
                return render_template(
                    'movimento_crediario/edit.html',
                    movimento=movimento,
                    grupos_crediario=grupos_crediario,
                    crediarios_disponiveis=crediarios_disponiveis,
                    today_date_str=today_date_str,
                    current_month_str=current_month_str
                )

            MovimentoCrediario.update(
                movimento_id, data_compra, descricao, id_grupo_crediario, id_crediario,
                valor_total, num_parcelas, primeira_parcela, current_user.id
            )
            flash('Movimento de Crediário atualizado com sucesso!', 'success')
            return redirect(url_for('movimento_crediario.list_movimentos_crediario'))
        except ValueError as e:
            flash(f'Erro de validação: {e}', 'danger')
            # Renderiza o formulário com os valores padrão e a mensagem de erro
            return render_template(
                'movimento_crediario/edit.html',
                movimento=movimento,
                grupos_crediario=grupos_crediario,
                crediarios_disponiveis=crediarios_disponiveis,
                today_date_str=today_date_str,
                current_month_str=current_month_str
            )
        except Exception as e:
            print(f"Erro inesperado ao atualizar movimento de crediário: {e}")
            flash('Ocorreu um erro inesperado ao atualizar o movimento.', 'danger')
            # Renderiza o formulário com os valores padrão e a mensagem de erro
            return render_template(
                'movimento_crediario/edit.html',
                movimento=movimento,
                grupos_crediario=grupos_crediario,
                crediarios_disponiveis=crediarios_disponiveis,
                today_date_str=today_date_str,
                current_month_str=current_month_str
            )

    return render_template(
        'movimento_crediario/edit.html',
        movimento=movimento,
        grupos_crediario=grupos_crediario,
        crediarios_disponiveis=crediarios_disponiveis,
        today_date_str=today_date_str,
        current_month_str=current_month_str
    )


@movimento_crediario_bp.route('/delete/<int:movimento_id>', methods=['POST'])
@login_required
def delete_movimento_crediario(movimento_id):
    movimento = MovimentoCrediario.get_by_id(movimento_id, current_user.id)
    if not movimento:
        flash('Movimento de Crediário não encontrado ou você não tem permissão para excluí-lo.', 'danger')
        return redirect(url_for('movimento_crediario.list_movimentos_crediario'))

    if MovimentoCrediario.delete(movimento_id, current_user.id):
        flash('Movimento de Crediário excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir o movimento de crediário.', 'danger')
    return redirect(url_for('movimento_crediario.list_movimentos_crediario'))
