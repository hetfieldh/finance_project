import psycopg
from psycopg import OperationalError
from contextlib import contextmanager
import os

from psycopg.errors import UniqueViolation, UndefinedTable
from config import Config


def get_db_connection():
    # Captura as variáveis de ambiente ou usa valores padrão para desenvolvimento
    db_name = os.getenv('DB_NAME', 'financas_db')
    db_user = os.getenv('DB_USER', 'user_financas')
    # Use uma senha segura e variável de ambiente em produção
    db_password = os.getenv('DB_PASSWORD', 'your_password')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')

    try:
        conn = psycopg.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        return conn
    except psycopg.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        # Você pode lançar uma exceção ou lidar com o erro de outra forma
        raise RuntimeError(
            "Não foi possível conectar ao banco de dados.") from e


@contextmanager
def get_db_cursor(commit=False):
    conn = None  # Inicializa conn para garantir que esteja definida
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro na transação do banco de dados: {e}")
        raise  # Re-lança a exceção para que a rota possa tratá-la
    finally:
        if conn:
            conn.close()


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    with get_db_cursor(commit=commit) as cur:
        cur.execute(query, params)
        if fetchone:
            return cur.fetchone()
        if fetchall:
            return cur.fetchall()
        return True


def check_and_update_table_constraints():
    """
    Verifica e atualiza as constraints das tabelas, incluindo a coluna password_hash para 'users'.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print(
                "Não foi possível conectar ao banco de dados para verificar constraints.")
            return

        with conn.cursor() as cursor:
            check_users_table_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'password_hash';
            """
            cursor.execute(check_users_table_query)
            password_hash_column_exists = cursor.fetchone() is not None

            if not password_hash_column_exists:
                print(
                    "Coluna 'password_hash' não encontrada na tabela 'users'. Tentando adicionar...")
                try:
                    cursor.execute(
                        "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);")
                    conn.commit()
                    print("Coluna 'password_hash' adicionada à tabela 'users'.")
                except Exception as e:
                    print(
                        f"Erro ao adicionar coluna 'password_hash' à tabela 'users': {e}")
                    print("Se a tabela 'users' já contém dados e a adição falhou (ex: NOT NULL sem padrão), pode ser necessário recriá-la ou preencher valores nulos manualmente.")
            else:
                print("Coluna 'password_hash' já existe na tabela 'users'.")

    except OperationalError as e:
        print(f"Erro de conexão durante a verificação de constraints: {e}")
    except UndefinedTable:
        print("Alguma tabela ainda não existe, a lógica de create_table() deve criá-la.")
    except Exception as e:
        print(
            f"Erro inesperado durante a verificação/correção das constraints: {e}")
    finally:
        if conn:
            conn.close()
