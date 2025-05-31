from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.crediario_model import Crediario
from psycopg.errors import UniqueViolation  # Importa a exceção específica
from flask_login import login_required, current_user

crediario_bp = Blueprint('crediarios', __name__, url_prefix='/crediarios')

TIPOS_CREDIARIO = ["Físico", "Virtual Recorrente",
                   "Virtual Temporário", "Outros"]


@crediario_bp.route('/')
@login_required
def list_crediarios():
    """Exibe uma lista de todos os crediários."""
    crediarios = Crediario.get_all()
    return render_template('crediarios/list.html', crediarios=crediarios)


@crediario_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_crediario():
    """Adiciona um novo crediário."""
    if request.method == 'POST':
        nome_crediario = request.form['nome_crediario']
        tipo = request.form['tipo']
        final = request.form['final']
        limite = request.form['limite']

        if not (nome_crediario and tipo and final and limite):
            flash('Todos os campos são obrigatórios!', 'warning')
        elif tipo not in TIPOS_CREDIARIO:
            flash(
                'Tipo de crediário inválido. Escolha uma das opções fornecidas.', 'warning')
        else:
            try:
                final_int = int(final)
                limite_float = float(limite)

                if len(nome_crediario) > 15:
                    flash('Nome do Crediário deve ter no máximo 15 dígitos.', 'warning')
                elif not (1000 <= final_int <= 9999):
                    flash('Final deve ser um número inteiro de 4 dígitos.', 'warning')
                else:
                    try:
                        new_crediario = Crediario.add(
                            nome_crediario, tipo, final_int, limite_float)
                        if new_crediario:
                            flash('Crediário adicionado com sucesso!', 'success')
                            return redirect(url_for('crediarios.list_crediarios'))
                        else:
                            # Isso só deve acontecer se execute_query retornar False por outro motivo
                            flash(
                                'Não foi possível adicionar o crediário. Verifique os logs do servidor.', 'danger')
                    except UniqueViolation:  # Captura a exceção específica de unicidade
                        flash(
                            'Erro: Já existe um crediário com esta combinação de Nome e Final.', 'danger')
                    except Exception as e:
                        print(f"Erro inesperado ao adicionar crediário: {e}")
                        flash(
                            'Ocorreu um erro inesperado ao adicionar o crediário. Verifique os logs do servidor.', 'danger')
            except ValueError:
                flash(
                    'Final deve ser um número inteiro e Limite deve ser um número válido.', 'warning')

    return render_template('crediarios/add.html', tipos_crediario=TIPOS_CREDIARIO)


@crediario_bp.route('/edit/<int:crediario_id>', methods=['GET', 'POST'])
@login_required
def edit_crediario(crediario_id):
    """Edita um crediário existente."""
    crediario = Crediario.get_by_id(crediario_id)
    if not crediario:
        flash('Crediário não encontrado.', 'danger')
        return redirect(url_for('crediarios.list_crediarios'))

    if request.method == 'POST':
        nome_crediario = request.form['nome_crediario']
        tipo = request.form['tipo']
        final = request.form['final']
        limite = request.form['limite']

        if not (nome_crediario and tipo and final and limite):
            flash('Todos os campos são obrigatórios!', 'warning')
        elif tipo not in TIPOS_CREDIARIO:
            flash(
                'Tipo de crediário inválido. Escolha uma das opções fornecidas.', 'warning')
        else:
            try:
                final_int = int(final)
                limite_float = float(limite)

                if len(nome_crediario) > 15:
                    flash('Nome do Crediário deve ter no máximo 15 dígitos.', 'warning')
                elif not (1000 <= final_int <= 9999):
                    flash('Final deve ser um número inteiro de 4 dígitos.', 'warning')
                else:
                    try:
                        updated_crediario = Crediario.update(
                            crediario_id, nome_crediario, tipo, final_int, limite_float)
                        if updated_crediario:
                            flash('Crediário atualizado com sucesso!', 'success')
                            return redirect(url_for('crediarios.list_crediarios'))
                        else:
                            flash(
                                'Não foi possível atualizar o crediário. Verifique os logs do servidor.', 'danger')
                    except UniqueViolation:
                        # Se tentar atualizar para uma combinação existente (nome_crediario, final)
                        flash(
                            'Erro: Já existe outro crediário com esta combinação de Nome e Final.', 'danger')
                    except Exception as e:
                        print(f"Erro inesperado ao atualizar crediário: {e}")
                        flash(
                            'Ocorreu um erro inesperado ao atualizar o crediário. Verifique os logs do servidor.', 'danger')
            except ValueError:
                flash(
                    'Final deve ser um número inteiro e Limite deve ser um número válido.', 'warning')

    return render_template('crediarios/edit.html', crediario=crediario, tipos_crediario=TIPOS_CREDIARIO)


@crediario_bp.route('/delete/<int:crediario_id>', methods=['POST'])
@login_required
def delete_crediario(crediario_id):
    """Exclui um crediário."""
    if Crediario.delete(crediario_id):
        flash('Crediário excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir crediário.', 'danger')
    return redirect(url_for('crediarios.list_crediarios'))
