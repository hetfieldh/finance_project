# models/movimento_bancario_model.py
from database.db_manager import execute_query, get_db_cursor
from datetime import datetime
from models.conta_bancaria_model import ContaBancaria


class MovimentoBancario:
    def __init__(self, id, conta_id, data, valor, descricao):
        self.id = id
        self.conta_id = conta_id
        self.data = data
        self.valor = valor
        self.descricao = descricao
        self.tipo = 'receita' if valor >= 0 else 'despesa'

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS movimentos_bancarios (
            id SERIAL PRIMARY KEY,
            conta_id INTEGER NOT NULL,
            data DATE NOT NULL,
            valor NUMERIC(15, 2) NOT NULL,
            descricao VARCHAR(255) NOT NULL,
            FOREIGN KEY (conta_id) REFERENCES contas_bancarias(id) ON DELETE CASCADE
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'movimentos_bancarios': {e}")
            raise

    @staticmethod
    def add(conta_id, data, valor, descricao):
        try:
            with get_db_cursor(commit=True) as cursor:
                conta = ContaBancaria.get_by_id(conta_id)
                if not conta:
                    raise ValueError("Conta bancária não encontrada.")

                novo_saldo = conta.saldo_atual + valor

                if valor < 0:
                    if novo_saldo < 0 and (conta.limite_credito is None or abs(novo_saldo) > conta.limite_credito):
                        raise ValueError(
                            f"Saldo insuficiente na conta [{conta.nome_banco} | {conta.tipo_conta} | {conta.numero_conta}] ou limite de crédito excedido.")

                cursor.execute(
                    'INSERT INTO movimentos_bancarios (conta_id, data, valor, descricao) VALUES (%s, %s, %s, %s) RETURNING id',
                    (conta_id, data, valor, descricao)
                )
                movimento_id = cursor.fetchone()[0]

                cursor.execute(
                    'UPDATE contas_bancarias SET saldo_atual = %s WHERE id = %s',
                    (novo_saldo, conta_id)
                )
                return MovimentoBancario(movimento_id, conta_id, data, valor, descricao)
        except Exception as e:
            raise e

    @staticmethod
    def transfer(conta_origem_id, conta_destino_id, valor, descricao):
        if valor <= 0:
            raise ValueError("O valor da transferência deve ser positivo.")

        try:
            with get_db_cursor(commit=True) as cursor:
                MovimentoBancario.add_internal(
                    cursor, conta_origem_id, datetime.now().date(), -valor, descricao)

                MovimentoBancario.add_internal(
                    cursor, conta_destino_id, datetime.now().date(), valor, descricao)

                return True
        except Exception as e:
            raise e

    @staticmethod
    def add_internal(cursor, conta_id, data, valor, descricao):
        conta = ContaBancaria.get_by_id(
            conta_id)
        if not conta:
            raise ValueError(
                f"Conta bancária com ID {conta_id} não encontrada para lançamento interno.")

        novo_saldo = conta.saldo_atual + valor

        if valor < 0:
            if novo_saldo < 0 and (conta.limite_credito is None or abs(novo_saldo) > conta.limite_credito):
                raise ValueError(
                    f"Saldo insuficiente na conta [{conta.nome_banco} | {conta.tipo_conta} | {conta.numero_conta}] ou limite de crédito excedido.")

        cursor.execute(
            'INSERT INTO movimentos_bancarios (conta_id, data, valor, descricao) VALUES (%s, %s, %s, %s)',
            (conta_id, data, valor, descricao)
        )
        cursor.execute(
            'UPDATE contas_bancarias SET saldo_atual = %s WHERE id = %s',
            (novo_saldo, conta_id)
        )

    @staticmethod
    def get_all_by_conta(conta_id):
        query = 'SELECT id, conta_id, data, valor, descricao FROM movimentos_bancarios WHERE conta_id = %s ORDER BY data DESC, id DESC'
        rows = execute_query(query, (conta_id,), fetchall=True)
        return [MovimentoBancario(row[0], row[1], row[2], float(row[3]), row[4]) for row in rows] if rows else []

    @staticmethod
    def get_extrato_mensal(conta_id, ano, mes):
        query = '''
        SELECT id, conta_id, data, valor, descricao
        FROM movimentos_bancarios
        WHERE conta_id = %s AND EXTRACT(YEAR FROM data) = %s AND EXTRACT(MONTH FROM data) = %s
        ORDER BY data ASC, id ASC
        '''
        rows = execute_query(query, (conta_id, ano, mes), fetchall=True)
        return [MovimentoBancario(row[0], row[1], row[2], float(row[3]), row[4]) for row in rows] if rows else []

    @staticmethod
    def get_saldo_inicial_do_mes(conta_id, ano, mes):
        query = '''
        SELECT COALESCE(SUM(valor), 0.0) FROM movimentos_bancarios
        WHERE conta_id = %s AND data < %s
        '''
        data_limite = datetime(ano, mes, 1).strftime('%Y-%m-%d')
        saldo = execute_query(query, (conta_id, data_limite), fetchone=True)
        return float(saldo[0]) if saldo and saldo[0] is not None else 0.0

    @staticmethod
    def get_by_id(movimento_id):
        query = 'SELECT id, conta_id, data, valor, descricao FROM movimentos_bancarios WHERE id = %s'
        row = execute_query(query, (movimento_id,), fetchone=True)
        return MovimentoBancario(row[0], row[1], row[2], float(row[3]), row[4]) if row else None

    @staticmethod
    def delete(movimento_id, user_id):
        try:
            with get_db_cursor(commit=True) as cursor:
                movimento = MovimentoBancario.get_by_id(movimento_id)
                if not movimento:
                    raise ValueError("Movimento bancário não encontrado.")

                conta = ContaBancaria.get_by_id(movimento.conta_id)
                if not conta or conta.user_id != user_id:
                    raise ValueError(
                        "Conta não encontrada ou você não tem permissão para esta conta.")

                novo_saldo = conta.saldo_atual - movimento.valor

                cursor.execute(
                    'UPDATE contas_bancarias SET saldo_atual = %s WHERE id = %s',
                    (novo_saldo, conta.id)
                )

                cursor.execute(
                    'DELETE FROM movimentos_bancarios WHERE id = %s',
                    (movimento_id,)
                )
                return True
        except Exception as e:
            raise e
