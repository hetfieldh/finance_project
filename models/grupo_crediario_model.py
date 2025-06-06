# models/grupo_crediario_model.py
from database.db_manager import execute_query
from psycopg.errors import UniqueViolation


class GrupoCrediario():
    def __init__(self, id, grupo, tipo, user_id):
        self.id = id
        self.grupo = grupo
        self.tipo = tipo
        self.user_id = user_id

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS grupo_crediario (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            grupo VARCHAR(255) NOT NULL,
            tipo VARCHAR (10) NOT NULL CHECK (tipo IN ('Compra', 'Estorno')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id, grupo, tipo)
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'grupo_crediario': {e}")
            raise

    @staticmethod
    def get_all_for_user(user_id):
        query = "SELECT id, grupo, tipo, user_id FROM grupo_crediario WHERE user_id = %s ORDER BY grupo ASC;"
        rows = execute_query(query, (user_id,), fetchall=True)

        if rows:
            return [GrupoCrediario(row[0], row[1], row[2], row[3]) for row in rows]
        return []

    @staticmethod
    def get_by_id(grupo_id, user_id):
        query = "SELECT id, grupo, tipo, user_id FROM grupo_crediario WHERE id = %s AND user_id = %s;"
        row = execute_query(query, (grupo_id, user_id), fetchone=True)
        if row:
            return GrupoCrediario(row[0], row[1], row[2], row[3])
        return None

    @staticmethod
    def add(grupo, tipo, user_id):
        if tipo not in ('Compra', 'Estorno'):
            raise ValueError(
                "Grupo de Crediário inválido. Deve ser 'Compra' ou 'Estorno'.")
        query = "INSERT INTO grupo_crediario (grupo, tipo, user_id) VALUES (%s, %s, %s) RETURNING id;"
        try:
            result = execute_query(
                query, (grupo, tipo, user_id), fetchone=True, commit=True)
            if result:
                return GrupoCrediario(result[0], grupo, tipo, user_id)
            return None
        except UniqueViolation:
            raise ValueError(
                f"O grupo '{grupo}' do tipo '{tipo}' já existe para este usuário.")
        except Exception as e:
            print(f"Erro ao adicionar grupo de crediário: {e}") 
            raise

    @staticmethod
    def update(grupo_id, grupo, tipo, user_id):
        if tipo not in ('Compra', 'Estorno'):
            raise ValueError(
                "Grupo de Crediário inválido. Deve ser 'Compra' ou 'Estorno'.")
        query = "UPDATE grupo_crediario SET grupo = %s, tipo = %s WHERE id = %s AND user_id = %s;"
        try:
            execute_query(
                query, (grupo, tipo, grupo_id, user_id), commit=True)
            return GrupoCrediario.get_by_id(grupo_id, user_id)
        except UniqueViolation:
            raise ValueError(
                f"O grupo '{grupo}' do tipo '{tipo}' já existe para este usuário.")
        except Exception as e:
            print(f"Erro ao atualizar o grupo de crediário: {e}")
            raise

    @staticmethod
    def delete(grupo_id, user_id):
        query = "DELETE FROM grupo_crediario WHERE id = %s AND user_id = %s;"
        execute_query(query, (grupo_id, user_id), commit=True)
        return True
