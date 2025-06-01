from database.db_manager import execute_query
from psycopg.errors import UniqueViolation


class Transacao:
    def __init__(self, id, transacao, tipo):
        self.id = id
        self.transacao = transacao
        self.tipo = tipo  # 'Entrada' ou 'Saída'

    @staticmethod
    def create_table():
        """Cria a tabela 'transacoes' se ela não existir."""
        query = """
        CREATE TABLE IF NOT EXISTS transacoes (
            id SERIAL PRIMARY KEY,
            transacao VARCHAR(100) NOT NULL,
            tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('Entrada', 'Saída')),
            UNIQUE (transacao, tipo)
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(f"ERRO CRÍTICO ao criar/verificar tabela 'transacoes': {e}")
            raise

    @staticmethod
    def get_all():
        """Retorna todas as transações cadastradas."""
        query = "SELECT id, transacao, tipo FROM transacoes ORDER BY transacao ASC;"
        rows = execute_query(query, fetchall=True)

        if rows:
            return [Transacao(row[0], row[1], row[2]) for row in rows]
        return []

    @staticmethod
    def get_by_id(transacao_id):
        """Retorna uma transação pelo ID."""
        query = "SELECT id, transacao, tipo FROM transacoes WHERE id = %s;"
        row = execute_query(query, (transacao_id,), fetchone=True)
        if row:
            return Transacao(row[0], row[1], row[2])
        return None

    @staticmethod
    def add(transacao, tipo):
        """Adiciona uma nova transação."""
        if tipo not in ('Entrada', 'Saída'):
            raise ValueError(
                "Tipo de transação inválido. Deve ser 'Entrada' ou 'Saída'.")
        query = "INSERT INTO transacoes (transacao, tipo) VALUES (%s, %s) RETURNING id;"
        try:
            result = execute_query(
                query, (transacao, tipo), fetchone=True, commit=True)
            if result:
                return Transacao(result[0], transacao, tipo)
            return None
        except UniqueViolation:
            raise ValueError(f"A transação '{transacao}' já existe.")
        except Exception as e:
            print(f"Erro ao adicionar transação: {e}")
            raise

    @staticmethod
    def update(transacao_id, transacao, tipo):
        """Atualiza uma transação existente."""
        if tipo not in ('Entrada', 'Saída'):
            raise ValueError(
                "Tipo de transação inválido. Deve ser 'Entrada' ou 'Saída'.")
        query = "UPDATE transacoes SET transacao = %s, tipo = %s WHERE id = %s;"
        try:
            execute_query(query, (transacao, tipo, transacao_id), commit=True)
            return Transacao.get_by_id(transacao_id)
        except UniqueViolation:
            raise ValueError(f"A transação '{transacao}' já existe.")
        except Exception as e:
            print(f"Erro ao atualizar transação: {e}")
            raise

    @staticmethod
    def delete(transacao_id):
        """Exclui uma transação pelo ID."""
        query = "DELETE FROM transacoes WHERE id = %s;"
        execute_query(query, (transacao_id,), commit=True)
        return True
