# models/transacao_model.py
from database.db_manager import execute_query
from psycopg.errors import UniqueViolation


class Transacao:
    def __init__(self, id, transacao, tipo, user_id):
        self.id = id
        self.transacao = transacao
        self.tipo = tipo
        self.user_id = user_id

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS transacoes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            transacao VARCHAR(100) NOT NULL,
            tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('Entrada', 'Saída')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id, transacao, tipo) -- Garante unicidade da transação por usuário e tipo
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(f"ERRO CRÍTICO ao criar/verificar tabela 'transacoes': {e}")
            raise

    @staticmethod
    def get_all_for_user(user_id):
        query = "SELECT id, transacao, tipo, user_id FROM transacoes WHERE user_id = %s ORDER BY transacao ASC;"
        rows = execute_query(query, (user_id,), fetchall=True)

        if rows:
            return [Transacao(row[0], row[1], row[2], row[3]) for row in rows]
        return []

    @staticmethod
    def get_by_id(transacao_id, user_id):
        query = "SELECT id, transacao, tipo, user_id FROM transacoes WHERE id = %s AND user_id = %s;"
        row = execute_query(query, (transacao_id, user_id), fetchone=True)
        if row:
            return Transacao(row[0], row[1], row[2], row[3])
        return None

    @staticmethod
    def add(transacao, tipo, user_id):
        if tipo not in ('Entrada', 'Saída'):
            raise ValueError(
                "Tipo de transação inválido. Deve ser 'Entrada' ou 'Saída'.")
        query = "INSERT INTO transacoes (transacao, tipo, user_id) VALUES (%s, %s, %s) RETURNING id;"
        try:
            result = execute_query(
                query, (transacao, tipo, user_id), fetchone=True, commit=True)
            if result:
                return Transacao(result[0], transacao, tipo, user_id)
            return None
        except UniqueViolation:
            raise ValueError(
                f"A transação '{transacao}' do tipo '{tipo}' já existe para este usuário.")
        except Exception as e:
            print(f"Erro ao adicionar transação: {e}")
            raise

    @staticmethod
    def update(transacao_id, transacao, tipo, user_id):
        if tipo not in ('Entrada', 'Saída'):
            raise ValueError(
                "Tipo de transação inválido. Deve ser 'Entrada' ou 'Saída'.")
        query = "UPDATE transacoes SET transacao = %s, tipo = %s WHERE id = %s AND user_id = %s;"
        try:
            execute_query(
                query, (transacao, tipo, transacao_id, user_id), commit=True)
            return Transacao.get_by_id(transacao_id, user_id)
        except UniqueViolation:
            raise ValueError(
                f"A transação '{transacao}' do tipo '{tipo}' já existe para este usuário.")
        except Exception as e:
            print(f"Erro ao atualizar transação: {e}")
            raise

    @staticmethod
    def delete(transacao_id, user_id):
        query = "DELETE FROM transacoes WHERE id = %s AND user_id = %s;"
        execute_query(query, (transacao_id, user_id), commit=True)
        return True
