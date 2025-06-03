# models/tipo_crediario_model.py
from database.db_manager import execute_query
from psycopg.errors import UniqueViolation


class TipoCrediario:
    def __init__(self, id, user_id, nome_tipo):
        self.id = id
        self.user_id = user_id
        self.nome_tipo = nome_tipo

    @staticmethod
    def create_table():
        """Cria a tabela 'tipos_crediario' se ela não existir."""
        query = """
        CREATE TABLE IF NOT EXISTS tipos_crediario (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            nome_tipo VARCHAR(100) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id, nome_tipo) -- Garante unicidade do tipo por usuário
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'tipos_crediario': {e}")
            raise

    @staticmethod
    def get_all_for_user(user_id):
        """Retorna todos os tipos de crediário cadastrados para um usuário específico."""
        query = "SELECT id, user_id, nome_tipo FROM tipos_crediario WHERE user_id = %s ORDER BY nome_tipo ASC;"
        rows = execute_query(query, (user_id,), fetchall=True)
        if rows:
            return [TipoCrediario(row[0], row[1], row[2]) for row in rows]
        return []

    @staticmethod
    def get_by_id(tipo_id, user_id):
        """Retorna um tipo de crediário pelo ID e user_id."""
        query = "SELECT id, user_id, nome_tipo FROM tipos_crediario WHERE id = %s AND user_id = %s;"
        row = execute_query(query, (tipo_id, user_id), fetchone=True)
        if row:
            return TipoCrediario(row[0], row[1], row[2])
        return None

    @staticmethod
    def add(user_id, nome_tipo):
        """Adiciona um novo tipo de crediário para um usuário específico."""
        query = "INSERT INTO tipos_crediario (user_id, nome_tipo) VALUES (%s, %s) RETURNING id;"
        try:
            result = execute_query(
                query, (user_id, nome_tipo), fetchone=True, commit=True)
            if result:
                return TipoCrediario(result[0], user_id, nome_tipo)
            return None
        except UniqueViolation:
            raise ValueError(
                f"O tipo de crediário '{nome_tipo}' já existe para este usuário.")
        except Exception as e:
            print(f"Erro ao adicionar tipo de crediário: {e}")
            raise

    @staticmethod
    def update(tipo_id, nome_tipo, user_id):
        """Atualiza um tipo de crediário existente para um usuário específico."""
        query = "UPDATE tipos_crediario SET nome_tipo = %s WHERE id = %s AND user_id = %s;"
        try:
            execute_query(query, (nome_tipo, tipo_id, user_id), commit=True)
            return TipoCrediario.get_by_id(tipo_id, user_id)
        except UniqueViolation:
            raise ValueError(
                f"O tipo de crediário '{nome_tipo}' já existe para este usuário.")
        except Exception as e:
            print(f"Erro ao atualizar tipo de crediário: {e}")
            raise

    @staticmethod
    def delete(tipo_id, user_id):
        """Exclui um tipo de crediário pelo ID e user_id."""
        query = "DELETE FROM tipos_crediario WHERE id = %s AND user_id = %s;"
        execute_query(query, (tipo_id, user_id), commit=True)
        return True
