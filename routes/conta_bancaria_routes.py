from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.conta_bancaria_model import ContaBancaria
from psycopg.errors import UniqueViolation
from flask_login import login_required, current_user

conta_bancaria_bp = Blueprint(
    'contas_bancarias', __name__, url_prefix='/contas_bancarias')

TIPOS_CONTA = ["Corrente", "Poupança", "Investimento",
               "Digital", "Restituições", "Vendas", "Serviços", "Outros"]

# --- Funções Auxiliares de Validação e Formatação (Back-end) ---


def format_and_validate_agencia(agencia_str):
    agencia_str = agencia_str.replace(" ", "").strip()
    if not agencia_str.isdigit():
        return None, "Agência deve conter apenas dígitos."
    if len(agencia_str) != 4:
        return None, "Agência deve ter exatamente 4 dígitos."
    return int(agencia_str), None


def format_and_validate_numero_conta(numero_conta_str):
    numero_conta_str = numero_conta_str.replace(" ", "").strip()
    if not numero_conta_str.isdigit():
        return None, "Número da Conta deve conter apenas dígitos."
    if not (1 <= len(numero_conta_str) <= 50):
        return None, "Número da Conta deve ter entre 1 e 50 dígitos."
    return numero_conta_str, None

# --- Rotas ---


@conta_bancaria_bp.route('/')
@login_required
def list_contas_bancarias():
    contas = ContaBancaria.get_all_for_user(
        current_user.id)
    return render_template('contas_bancarias/list.html', contas=contas)


@conta_bancaria_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_conta_bancaria():
    if request.method == 'POST':
        nome_banco = request.form['nome_banco']
        agencia = request.form['agencia']
        numero_conta = request.form['numero_conta']
        tipo_conta = request.form['tipo_conta']
        saldo_inicial = request.form['saldo_inicial']
        limite_credito = request.form.get('limite_credito')

        if not (nome_banco and agencia and numero_conta and tipo_conta and saldo_inicial):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'warning')
            return render_template('contas_bancarias/add.html', tipos_conta=TIPOS_CONTA)

        if tipo_conta not in TIPOS_CONTA:
            flash('Tipo de conta inválido. Escolha uma das opções fornecidas.', 'warning')
            return render_template('contas_bancarias/add.html', tipos_conta=TIPOS_CONTA)

        agencia_val, agencia_error = format_and_validate_agencia(agencia)
        if agencia_error:
            flash(agencia_error, 'warning')
            return render_template('contas_bancarias/add.html', tipos_conta=TIPOS_CONTA)

        numero_conta_val, num_conta_error = format_and_validate_numero_conta(
            numero_conta)
        if num_conta_error:
            flash(num_conta_error, 'warning')
            return render_template('contas_bancarias/add.html', tipos_conta=TIPOS_CONTA)

        try:
            saldo_inicial_float = float(saldo_inicial)
            limite_credito_float = float(
                limite_credito) if limite_credito else None

            if len(nome_banco) > 100:
                flash('Nome do Banco deve ter no máximo 100 caracteres.', 'warning')
                return render_template('contas_bancarias/add.html', tipos_conta=TIPOS_CONTA)

            new_conta = ContaBancaria.add(
                current_user.id,
                nome_banco, agencia_val, numero_conta_val, tipo_conta,
                saldo_inicial_float, limite_credito_float
            )
            if new_conta:
                flash('Conta adicionada com sucesso!', 'success')
                return redirect(url_for('contas_bancarias.list_contas_bancarias'))
            else:
                flash(
                    'Não foi possível adicionar a conta. Verifique os logs do servidor.', 'danger')
        except UniqueViolation:
            flash(
                'Erro: Já existe uma conta com esta combinação de Agência, Número da Conta e Tipo.', 'danger')
        except ValueError as e:
            flash(f'Erro de valor: {e}', 'warning')
        except Exception as e:
            print(f"Erro inesperado ao adicionar conta: {e}")
            flash(
                'Ocorreu um erro inesperado ao adicionar a conta. Verifique os logs do servidor.', 'danger')

    return render_template('contas_bancarias/add.html', tipos_conta=TIPOS_CONTA)


# <-- Blueprint name usado aqui
@conta_bancaria_bp.route('/edit/<int:conta_id>', methods=['GET', 'POST'])
@login_required
def edit_conta_bancaria(conta_id):
    conta = ContaBancaria.get_by_id(conta_id)
    if not conta or conta.user_id != current_user.id:
        flash('Conta não encontrada ou você não tem permissão para editá-la.', 'danger')
        return redirect(url_for('contas_bancarias.list_contas_bancarias'))

    if request.method == 'POST':
        nome_banco = request.form['nome_banco']
        agencia = request.form['agencia']
        numero_conta = request.form['numero_conta']
        tipo_conta = request.form['tipo_conta']
        saldo_inicial = request.form['saldo_inicial']
        saldo_atual = request.form['saldo_atual']
        limite_credito = request.form.get('limite_credito')

        if not (nome_banco and agencia and numero_conta and tipo_conta and saldo_inicial and saldo_atual):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'warning')
            return render_template('contas_bancarias/edit.html', conta=conta, tipos_conta=TIPOS_CONTA)

        if tipo_conta not in TIPOS_CONTA:
            flash('Tipo de conta inválido. Escolha uma das opções fornecidas.', 'warning')
            return render_template('contas_bancarias/edit.html', conta=conta, tipos_conta=TIPOS_CONTA)

        agencia_val, agencia_error = format_and_validate_agencia(agencia)
        if agencia_error:
            flash(agencia_error, 'warning')
            return render_template('contas_bancarias/edit.html', conta=conta, tipos_conta=TIPOS_CONTA)

        numero_conta_val, num_conta_error = format_and_validate_numero_conta(
            numero_conta)
        if num_conta_error:
            flash(num_conta_error, 'warning')
            return render_template('contas_bancarias/edit.html', conta=conta, tipos_conta=TIPOS_CONTA)

        try:
            saldo_inicial_float = float(saldo_inicial)
            saldo_atual_float = float(saldo_atual)
            limite_credito_float = float(
                limite_credito) if limite_credito else None

            if len(nome_banco) > 100:
                flash('Nome do Banco deve ter no máximo 100 caracteres.', 'warning')
                return render_template('contas_bancarias/edit.html', conta=conta, tipos_conta=TIPOS_CONTA)

            updated_conta = ContaBancaria.update(
                conta_id, nome_banco, agencia_val, numero_conta_val, tipo_conta,
                saldo_inicial_float, saldo_atual_float, limite_credito_float
            )
            if updated_conta:
                flash('Conta atualizada com sucesso!', 'success')
                return redirect(url_for('contas_bancarias.list_contas_bancarias'))
            else:
                flash(
                    'Não foi possível atualizar a conta. Verifique os logs do servidor.', 'danger')
        except UniqueViolation:
            flash(
                'Erro: Já existe outra conta com esta combinação de Agência, Número da Conta e Tipo.', 'danger')
        except ValueError as e:
            flash(f'Erro de valor: {e}', 'warning')
        except Exception as e:
            print(f"Erro inesperado ao atualizar conta: {e}")
            flash(
                'Ocorreu um erro inesperado ao atualizar a conta. Verifique os logs do servidor.', 'danger')

    return render_template('contas_bancarias/edit.html', conta=conta, tipos_conta=TIPOS_CONTA)


# <-- Blueprint name usado aqui
@conta_bancaria_bp.route('/delete/<int:conta_id>', methods=['POST'])
@login_required
def delete_conta_bancaria(conta_id):
    conta = ContaBancaria.get_by_id(conta_id)
    if not conta or conta.user_id != current_user.id:
        flash('Conta não encontrada ou você não tem permissão para excluí-la.', 'danger')
        return redirect(url_for('contas_bancarias.list_contas_bancarias'))

    if ContaBancaria.delete(conta_id):
        flash('Conta excluída com sucesso!', 'success')
    else:
        flash('Erro ao excluir conta.', 'danger')
    return redirect(url_for('contas_bancarias.list_contas_bancarias'))
