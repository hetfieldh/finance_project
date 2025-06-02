from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.transacao_model import Transacao
from flask_login import login_required, current_user  # Importa current_user


transacao_bp = Blueprint('transacoes', __name__, url_prefix='/transacoes')

TIPOS_TRANSACAO = ["Entrada", "Saída"]


@transacao_bp.route('/')
@login_required
def list_transacoes():
    # Busca apenas as transações do usuário logado
    transacoes = Transacao.get_all_for_user(current_user.id)
    return render_template('transacoes/list.html', transacoes=transacoes)


@transacao_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transacao():
    if request.method == 'POST':
        transacao_nome = request.form['transacao']
        tipo = request.form['tipo']

        if not (transacao_nome and tipo):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template('transacoes/add.html', tipos_transacao=TIPOS_TRANSACAO)

        if tipo not in TIPOS_TRANSACAO:
            flash('Tipo de transação inválido.', 'warning')
            return render_template('transacoes/add.html', tipos_transacao=TIPOS_TRANSACAO)

        try:
            # Adiciona a transação para o usuário logado
            Transacao.add(transacao_nome, tipo, current_user.id)
            flash('Transação adicionada com sucesso!', 'success')
            return redirect(url_for('transacoes.list_transacoes'))
        except ValueError as e:
            flash(f'Erro: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao adicionar transação: {e}")
            flash('Ocorreu um erro inesperado ao adicionar a transação.', 'danger')

    return render_template('transacoes/add.html', tipos_transacao=TIPOS_TRANSACAO)


@transacao_bp.route('/edit/<int:transacao_id>', methods=['GET', 'POST'])
@login_required
def edit_transacao(transacao_id):
    # Busca a transação pelo ID e pelo user_id para garantir que o usuário só edite as suas
    transacao = Transacao.get_by_id(transacao_id, current_user.id)
    if not transacao:
        flash('Transação não encontrada ou você não tem permissão para editá-la.', 'danger')
        return redirect(url_for('transacoes.list_transacoes'))

    if request.method == 'POST':
        transacao_nome = request.form['transacao']
        tipo = request.form['tipo']

        if not (transacao_nome and tipo):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template('transacoes/edit.html', transacao=transacao, tipos_transacao=TIPOS_TRANSACAO)

        if tipo not in TIPOS_TRANSACAO:
            flash('Tipo de transação inválido.', 'warning')
            return render_template('transacoes/edit.html', transacao=transacao, tipos_transacao=TIPOS_TRANSACAO)

        try:
            # Atualiza a transação, passando o user_id para a validação
            Transacao.update(transacao_id, transacao_nome,
                             tipo, current_user.id)
            flash('Transação atualizada com sucesso!', 'success')
            return redirect(url_for('transacoes.list_transacoes'))
        except ValueError as e:
            flash(f'Erro: {e}', 'danger')
        except Exception as e:
            print(f"Erro inesperado ao atualizar transação: {e}")
            flash('Ocorreu um erro inesperado ao atualizar a transação.', 'danger')

    return render_template('transacoes/edit.html', transacao=transacao, tipos_transacao=TIPOS_TRANSACAO)


@transacao_bp.route('/delete/<int:transacao_id>', methods=['POST'])
@login_required
def delete_transacao(transacao_id):
    # Busca a transação pelo ID e pelo user_id para garantir que o usuário só exclua as suas
    transacao = Transacao.get_by_id(transacao_id, current_user.id)
    if not transacao:
        flash(
            'Transação não encontrada ou você não tem permissão para excluí-la.', 'danger')
        return redirect(url_for('transacoes.list_transacoes'))

    # Exclui a transação, passando o user_id para a validação
    if Transacao.delete(transacao_id, current_user.id):
        flash('Transação excluída com sucesso!', 'success')
    else:
        flash('Erro ao excluir transação.', 'danger')
    return redirect(url_for('transacoes.list_transacoes'))
