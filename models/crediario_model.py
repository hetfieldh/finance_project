# models/crediario_model.py
from database.db_manager import execute_query
from psycopg.errors import UniqueViolation


class Crediario:
    def __init__(self, id, crediario, tipo, final, limite, user_id):
        self.id = id
        self.crediario = crediario
        self.tipo = tipo
        self.final = final
        self.limite = limite
        self.user_id = user_id 

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS crediarios (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL, -- Campo para vincular ao usuário
            crediario VARCHAR(100) NOT NULL,
            tipo VARCHAR(100) NOT NULL,
            final INTEGER NOT NULL,
            limite NUMERIC(10, 2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, -- Chave estrangeira
            UNIQUE(user_id, crediario, final) -- Unicidade por usuário, crediario e final
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(f"ERRO CRÍTICO ao criar/verificar tabela 'crediarios': {e}")
            raise

    @staticmethod
    def get_all_for_user(user_id):
        query = "SELECT id, crediario, tipo, final, limite, user_id FROM crediarios WHERE user_id = %s ORDER BY crediario ASC;"
        rows = execute_query(query, (user_id,), fetchall=True)
        if rows:
            return [Crediario(row[0], row[1], row[2], row[3], float(row[4]), row[5]) for row in rows]
        return []

    @staticmethod
    def get_by_id(crediario_id, user_id):
        query = "SELECT id, crediario, tipo, final, limite, user_id FROM crediarios WHERE id = %s AND user_id = %s;"
        row = execute_query(query, (crediario_id, user_id), fetchone=True)
        if row:
            return Crediario(row[0], row[1], row[2], row[3], float(row[4]), row[5])
        return None

    @staticmethod
    def add(crediario, tipo, final, limite, user_id):
        query = "INSERT INTO crediarios (crediario, tipo, final, limite, user_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;"
        try:
            result = execute_query(
                query, (crediario, tipo, final, limite, user_id), fetchone=True, commit=True)
            if result:
                return Crediario(result[0], crediario, tipo, final, limite, user_id)
            return None
        except UniqueViolation:
            raise ValueError(
                f"Já existe um crediário com este nome e final para este usuário.")
        except Exception as e:
            print(f"Erro ao adicionar crediário: {e}")
            raise

    @staticmethod
    def update(crediario_id, crediario_val, tipo, final, limite, user_id):
        query = "UPDATE crediarios SET crediario = %s, tipo = %s, final = %s, limite = %s WHERE id = %s AND user_id = %s;"
        try:
            execute_query(query, (crediario_val, tipo, final,
                          limite, crediario_id, user_id), commit=True)
            return Crediario.get_by_id(crediario_id, user_id)
        except UniqueViolation:
            raise ValueError(
                f"Já existe outro crediário com este nome e final para este usuário.")
        except Exception as e:
            print(f"Erro ao atualizar crediário: {e}")
            raise

    @staticmethod
    def delete(crediario_id, user_id):
        query = "DELETE FROM crediarios WHERE id = %s AND user_id = %s;"
        execute_query(query, (crediario_id, user_id), commit=True)
        return True
