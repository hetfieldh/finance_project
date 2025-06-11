# models/despesa_fixa_model.py
from database.db_manager import execute_query
from psycopg.errors import UniqueViolation
from datetime import date


class DespesaFixa:
    def __init__(self, id, user_id, descricao, mes_ano, valor):
        self.id = id
        self.user_id = user_id
        self.descricao = descricao
        self.mes_ano = mes_ano
        self.valor = valor

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS despesas_fixas (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            descricao VARCHAR(100) NOT NULL,
            mes_ano DATE NOT NULL,
            valor DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, descricao, mes_ano)
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'despesas_fixas': {e}")
            raise

    @staticmethod
    def get_all_for_user(user_id):
        query = """
        SELECT id, user_id, descricao, mes_ano, valor
        FROM despesas_fixas
        WHERE user_id = %s
        ORDER BY mes_ano DESC, descricao ASC;
        """
        rows = execute_query(query, (user_id,), fetchall=True)
        if rows:
            return [DespesaFixa(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return []

    @staticmethod
    def get_by_id(despesa_id, user_id):
        query = """
        SELECT id, user_id, descricao, mes_ano, valor
        FROM despesas_fixas
        WHERE id = %s AND user_id = %s;
        """
        row = execute_query(query, (despesa_id, user_id), fetchone=True)
        if row:
            return DespesaFixa(row[0], row[1], row[2], row[3], row[4])
        return None

    @staticmethod
    def add(user_id, descricao, mes_ano, valor):
        query = """
        INSERT INTO despesas_fixas (user_id, descricao, mes_ano, valor)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """
        try:
            result = execute_query(
                query, (user_id, descricao, mes_ano, valor), fetchone=True, commit=True)
            if result:
                return DespesaFixa(result[0], user_id, descricao, mes_ano, valor)
            return None
        except UniqueViolation:
            raise ValueError(
                f"Já existe uma despesa fixa '{descricao}' para o mês/ano '{mes_ano.strftime('%m/%Y')}' para este usuário.")
        except Exception as e:
            print(f"Erro ao adicionar despesa fixa: {e}")
            raise

    @staticmethod
    def update(despesa_id, user_id, descricao, mes_ano, valor):
        query = """
        UPDATE despesas_fixas
        SET descricao = %s, mes_ano = %s, valor = %s
        WHERE id = %s AND user_id = %s;
        """
        params = (descricao, mes_ano, valor, despesa_id, user_id)
        try:
            execute_query(query, params, commit=True)
            return DespesaFixa.get_by_id(despesa_id, user_id)
        except UniqueViolation:
            raise ValueError(
                f"Já existe outra despesa fixa '{descricao}' para o mês/ano '{mes_ano.strftime('%m/%Y')}' para este usuário.")
        except Exception as e:
            print(f"Erro ao atualizar despesa fixa: {e}")
            raise

    @staticmethod
    def delete(despesa_id, user_id):
        query = "DELETE FROM despesas_fixas WHERE id = %s AND user_id = %s;"
        execute_query(query, (despesa_id, user_id), commit=True)
        return True
