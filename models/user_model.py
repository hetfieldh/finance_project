from database.db_manager import execute_query
from psycopg.errors import UniqueViolation
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, name, email, login, password_hash=None, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.login = login
        self.password_hash = password_hash
        self.is_admin = is_admin

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            login VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE 
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(f"ERRO CRÍTICO ao criar/verificar tabela 'users': {e}")
            raise

    # Métodos exigidos pelo Flask-Login

    def get_id(self):
        return str(self.id)  # Flask-Login exige que o ID seja uma string

    # Métodos para hash e verificação de senha
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_all(cls):
        rows = execute_query(
            "SELECT id, name, email, login, password_hash, is_admin FROM users ORDER BY name", fetchall=True)
        return [cls(*row) for row in rows] if rows else []

    @classmethod
    def get_by_id(cls, user_id):
        row = execute_query(
            "SELECT id, name, email, login, password_hash, is_admin FROM users WHERE id = %s", (user_id,), fetchone=True)
        return cls(*row) if row else None

    @classmethod
    def get_by_login(cls, login):
        row = execute_query(
            "SELECT id, name, email, login, password_hash, is_admin FROM users WHERE login = %s", (login,), fetchone=True)
        return cls(*row) if row else None

    @classmethod
    def add(cls, name, email, login, password, is_admin=False):
        password_hash = generate_password_hash(password)
        try:
            result = execute_query(
                "INSERT INTO users (name, email, login, password_hash, is_admin) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (name, email, login, password_hash, is_admin),
                fetchone=True,
                commit=True
            )
            if result:

                return cls(result[0], name, email, login, password_hash, is_admin)
            return None
        except UniqueViolation as e:
            raise ValueError(
                "Erro: Já existe um usuário com este login ou email.") from e

    @classmethod
    def update(cls, user_id, name, email, login, new_password=None, is_admin=None):
        user = cls.get_by_id(user_id)
        if not user:
            return None

        password_hash_to_save = user.password_hash
        if new_password:
            password_hash_to_save = generate_password_hash(new_password)

        is_admin_to_save = user.is_admin if is_admin is None else is_admin

        try:
            query = "UPDATE users SET name = %s, email = %s, login = %s, password_hash = %s, is_admin = %s WHERE id = %s"
            params = (name, email, login, password_hash_to_save,
                      is_admin_to_save, user_id)
            if execute_query(query, params, commit=True):
                return cls(user_id, name, email, login, password_hash_to_save, is_admin_to_save)
            return None
        except UniqueViolation as e:
            raise ValueError(
                "Erro: Já existe outro usuário com este login ou email.") from e

    @classmethod
    def delete(cls, user_id):
        query = "DELETE FROM users WHERE id = %s"
        params = (user_id,)
        return execute_query(query, params, commit=True)
