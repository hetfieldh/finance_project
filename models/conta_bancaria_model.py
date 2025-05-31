from database.db_manager import execute_query, get_db_cursor
from psycopg.errors import UniqueViolation


class ContaBancaria:
    def __init__(self, id, user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_atual, limite_credito):
        self.id = id
        self.user_id = user_id
        self.nome_banco = nome_banco
        self.agencia = agencia
        self.numero_conta = numero_conta
        self.tipo_conta = tipo_conta
        self.saldo_inicial = saldo_inicial
        self.saldo_atual = saldo_atual
        self.limite_credito = limite_credito

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS contas_bancarias (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            nome_banco VARCHAR(100) NOT NULL,
            agencia INTEGER NOT NULL,
            numero_conta VARCHAR(50) NOT NULL,
            tipo_conta VARCHAR(20) NOT NULL,
            saldo_inicial NUMERIC(15, 2) NOT NULL,
            saldo_atual NUMERIC(15, 2) NOT NULL,
            limite_credito NUMERIC(15, 2) NULL,
            UNIQUE(agencia, numero_conta, tipo_conta),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'contas_bancarias': {e}")
            raise

    @staticmethod
    def get_all():
        """Retorna todas as contas bancárias do banco de dados (sem filtro de usuário)."""
        query = "SELECT id, user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_atual, limite_credito FROM contas_bancarias ORDER BY nome_banco ASC, tipo_conta ASC;"
        rows = execute_query(query, fetchall=True)
        if rows:
            return [ContaBancaria(row[0], row[1], row[2], row[3], row[4], row[5], float(row[6]), float(row[7]), float(row[8]) if row[8] is not None else None) for row in rows]
        return []

    @staticmethod
    def get_all_for_user(user_id):
        """Retorna todas as contas bancárias de um usuário específico."""
        query = "SELECT id, user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_atual, limite_credito FROM contas_bancarias WHERE user_id = %s ORDER BY nome_banco ASC, tipo_conta ASC;"
        rows = execute_query(query, (user_id,), fetchall=True)
        if rows:
            return [ContaBancaria(row[0], row[1], row[2], row[3], row[4], row[5], float(row[6]), float(row[7]), float(row[8]) if row[8] is not None else None) for row in rows]
        return []

    @staticmethod
    def get_by_id(conta_id):
        """Retorna uma conta bancária pelo ID."""
        query = "SELECT id, user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_atual, limite_credito FROM contas_bancarias WHERE id = %s;"
        row = execute_query(query, (conta_id,), fetchone=True)
        if row:
            return ContaBancaria(row[0], row[1], row[2], row[3], row[4], row[5], float(row[6]), float(row[7]), float(row[8]) if row[8] is not None else None)
        return None

    @staticmethod
    def add(user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, limite_credito=None):
        """Adiciona uma nova conta bancária ao banco de dados."""
        query = """
        INSERT INTO contas_bancarias (user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_atual, limite_credito)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        result = execute_query(
            query, (user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_inicial, limite_credito), fetchone=True, commit=True)
        if result:
            return ContaBancaria(result[0], user_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_inicial, limite_credito)
        return None

    @staticmethod
    def update(conta_id, nome_banco, agencia, numero_conta, tipo_conta, saldo_inicial, saldo_atual, limite_credito):
        """Atualiza uma conta bancária existente. saldo_atual e limite_credito são atualizáveis."""
        query = """
        UPDATE contas_bancarias SET
        nome_banco = %s, agencia = %s, numero_conta = %s, tipo_conta = %s, saldo_inicial = %s, saldo_atual = %s, limite_credito = %s
        WHERE id = %s;
        """
        execute_query(query, (nome_banco, agencia, numero_conta, tipo_conta,
                              saldo_inicial, saldo_atual, limite_credito, conta_id), commit=True)
        return ContaBancaria.get_by_id(conta_id)

    @staticmethod
    def delete(conta_id):
        """Exclui uma conta bancária pelo ID."""
        query = "DELETE FROM contas_bancarias WHERE id = %s;"
        execute_query(query, (conta_id,), commit=True)
        return True
