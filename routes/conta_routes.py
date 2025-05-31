from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.conta_model import Conta
from psycopg.errors import UniqueViolation
from flask_login import login_required, current_user

conta_bp = Blueprint('contas', __name__, url_prefix='/contas')

TIPOS_CONTA = ["Corrente", "Poupança", "Investimento",
               "Digital", "Restituições", "Vendas", "Serviços", "Outros"]

# --- Funções Auxiliares de Validação e Formatação (Back-end) ---


def format_and_validate_agencia(agencia_str):
    """Valida e formata a agência para 4 dígitos com zeros à esquerda."""
    agencia_str = agencia_str.replace(" ", "").strip()  # Remove espaços
    if not agencia_str.isdigit():
        return None, "Agência deve conter apenas dígitos."
    if len(agencia_str) != 4:
        return None, "Agência deve ter exatamente 4 dígitos."
    return int(agencia_str), None  # Retorna como int


def format_and_validate_numero_conta(numero_conta_str):
    """Valida e formata o número da conta para 20 dígitos com zeros à esquerda."""
    numero_conta_str = numero_conta_str.replace(
        " ", "").strip()  # Remove espaços
    if not numero_conta_str.isdigit():
        return None, "Número da Conta deve conter apenas dígitos."
    if not (1 <= len(numero_conta_str) <= 20):  # Permite até 20 dígitos, mas com 1 mínimo
        return None, "Número da Conta deve ter entre 1 e 20 dígitos."
    # Preenche com zeros à esquerda se for menor que 20 dígitos
    formatted_num_conta = numero_conta_str.zfill(20)
    return int(formatted_num_conta), None  # Retorna como int (BIGINT no DB)

# --- Rotas ---


@conta_bp.route('/')
@login_required
def list_contas():
    contas = Conta.get_all()
    return render_template('contas_bancarias/list.html', contas=contas)


@conta_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_conta():
    if request.method == 'POST':
        nome_banco = request.form['nome_banco']
        agencia = request.form['agencia']
        numero_conta = request.form['numero_conta']
        tipo = request.form['tipo']
        saldo_inicial = request.form['saldo_inicial']
        limite = request.form['limite']

        if not (nome_banco and agencia and numero_conta and tipo and saldo_inicial and limite):
            flash('Todos os campos são obrigatórios!', 'warning')
            # Renderiza novamente com erro
            return render_template('add_conta.html', tipos_conta=TIPOS_CONTA)

        if tipo not in TIPOS_CONTA:
            flash('Tipo de conta inválido. Escolha uma das opções fornecidas.', 'warning')
            return render_template('add_conta.html', tipos_conta=TIPOS_CONTA)

        # Validação e formatação da agência
        agencia_val, agencia_error = format_and_validate_agencia(agencia)
        if agencia_error:
            flash(agencia_error, 'warning')
            return render_template('add_conta.html', tipos_conta=TIPOS_CONTA)

        # Validação e formatação do número da conta
        numero_conta_val, num_conta_error = format_and_validate_numero_conta(
            numero_conta)
        if num_conta_error:
            flash(num_conta_error, 'warning')
            return render_template('add_conta.html', tipos_conta=TIPOS_CONTA)

        try:
            saldo_inicial_float = float(saldo_inicial)
            limite_float = float(limite)

            if len(nome_banco) > 100:
                flash('Nome do Banco deve ter no máximo 100 caracteres.', 'warning')
                return render_template('add_conta.html', tipos_conta=TIPOS_CONTA)

            try:
                new_conta = Conta.add(
                    nome_banco, agencia_val, numero_conta_val, tipo, saldo_inicial_float, limite_float)
                if new_conta:
                    flash('Conta adicionada com sucesso!', 'success')
                    return redirect(url_for('contas.list_contas'))
                else:
                    flash(
                        'Não foi possível adicionar a conta. Verifique os logs do servidor.', 'danger')
            except UniqueViolation:
                flash(
                    'Erro: Já existe uma conta com esta combinação de Agência, Número da Conta e Tipo.', 'danger')
            except Exception as e:
                print(f"Erro inesperado ao adicionar conta: {e}")
                flash(
                    'Ocorreu um erro inesperado ao adicionar a conta. Verifique os logs do servidor.', 'danger')
        except ValueError:
            flash('Saldo Inicial e Limite devem ser números válidos.', 'warning')

    return render_template('contas_bancarias/add.html', tipos_conta=TIPOS_CONTA)


@conta_bp.route('/edit/<int:conta_id>', methods=['GET', 'POST'])
@login_required
def edit_conta(conta_id):
    conta = Conta.get_by_id(conta_id)
    if not conta:
        flash('Conta não encontrada.', 'danger')
        return redirect(url_for('contas.list_contas'))

    if request.method == 'POST':
        nome_banco = request.form['nome_banco']
        agencia = request.form['agencia']
        numero_conta = request.form['numero_conta']
        tipo = request.form['tipo']
        saldo_inicial = request.form['saldo_inicial']
        limite = request.form['limite']

        if not (nome_banco and agencia and numero_conta and tipo and saldo_inicial and limite):
            flash('Todos os campos são obrigatórios!', 'warning')
            return render_template('edit_conta.html', conta=conta, tipos_conta=TIPOS_CONTA)

        if tipo not in TIPOS_CONTA:
            flash('Tipo de conta inválido. Escolha uma das opções fornecidas.', 'warning')
            return render_template('edit_conta.html', conta=conta, tipos_conta=TIPOS_CONTA)

        # Validação e formatação da agência
        agencia_val, agencia_error = format_and_validate_agencia(agencia)
        if agencia_error:
            flash(agencia_error, 'warning')
            return render_template('edit_conta.html', conta=conta, tipos_conta=TIPOS_CONTA)

        # Validação e formatação do número da conta
        numero_conta_val, num_conta_error = format_and_validate_numero_conta(
            numero_conta)
        if num_conta_error:
            flash(num_conta_error, 'warning')
            return render_template('edit_conta.html', conta=conta, tipos_conta=TIPOS_CONTA)

        try:
            saldo_inicial_float = float(saldo_inicial)
            limite_float = float(limite)

            if len(nome_banco) > 100:
                flash('Nome do Banco deve ter no máximo 100 caracteres.', 'warning')
                return render_template('edit_conta.html', conta=conta, tipos_conta=TIPOS_CONTA)

            try:
                updated_conta = Conta.update(
                    conta_id, nome_banco, agencia_val, numero_conta_val, tipo, saldo_inicial_float, limite_float)
                if updated_conta:
                    flash('Conta atualizada com sucesso!', 'success')
                    return redirect(url_for('contas.list_contas'))
                else:
                    flash(
                        'Não foi possível atualizar a conta. Verifique os logs do servidor.', 'danger')
            except UniqueViolation:
                flash(
                    'Erro: Já existe outra conta com esta combinação de Agência, Número da Conta e Tipo.', 'danger')
            except Exception as e:
                print(f"Erro inesperado ao atualizar conta: {e}")
                flash(
                    'Ocorreu um erro inesperado ao atualizar a conta. Verifique os logs do servidor.', 'danger')
        except ValueError:
            flash('Saldo Inicial e Limite devem ser números válidos.', 'warning')

    return render_template('contas_bancarias/edit.html', conta=conta, tipos_conta=TIPOS_CONTA)


@conta_bp.route('/delete/<int:conta_id>', methods=['POST'])
@login_required
def delete_conta(conta_id):
    if Conta.delete(conta_id):
        flash('Conta excluída com sucesso!', 'success')
    else:
        flash('Erro ao excluir conta.', 'danger')
    return redirect(url_for('contas.list_contas'))
