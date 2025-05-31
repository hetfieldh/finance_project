import psycopg
from psycopg.errors import OperationalError, UniqueViolation, UndefinedTable
from config import Config
from contextlib import contextmanager


def get_db_connection():
    db_config = Config.DATABASE
    try:
        conn = psycopg.connect(
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port']
        )
        return conn
    except OperationalError as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        raise RuntimeError(
            "Não foi possível conectar ao banco de dados.") from e


@contextmanager
def get_db_cursor(commit=False):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro na transação do banco de dados: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    try:
        with get_db_cursor(commit=commit) as cursor:
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
            else:
                return True
    except OperationalError as e:
        print(f"Erro de operação no banco de dados: {e}")
        return False
    except UniqueViolation as e:
        print(f"Erro de violação de unicidade: {e}")
        raise ValueError("Violação de unicidade de dados.") from e
    except Exception as e:
        print(f"Erro inesperado ao executar consulta: {e}")
        raise


def check_and_update_table_constraints():
    """
    Verifica e atualiza as constraints das tabelas, incluindo a coluna password_hash para 'users'
    e 'saldo_atual', 'limite_credito' para 'contas_bancarias'.
    Imprime mensagens APENAS se uma alteração for feita ou um erro ocorrer.
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            # --- users table ---
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'password_hash';
            """)
            if not cursor.fetchone():
                print("Adicionando coluna 'password_hash' à tabela 'users'...")
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);")
                print("Coluna 'password_hash' adicionada à tabela 'users'.")

            # --- contas_bancarias table ---
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'contas_bancarias' AND column_name = 'saldo_atual';
            """)
            if not cursor.fetchone():
                print("Adicionando coluna 'saldo_atual' à tabela 'contas_bancarias'...")
                cursor.execute(
                    "ALTER TABLE contas_bancarias ADD COLUMN saldo_atual NUMERIC(15, 2) NOT NULL DEFAULT 0.0;")
                print("Coluna 'saldo_atual' adicionada à tabela 'contas_bancarias'.")

            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'contas_bancarias' AND column_name = 'limite_credito';
            """)
            if not cursor.fetchone():
                print(
                    "Adicionando coluna 'limite_credito' à tabela 'contas_bancarias'...")
                cursor.execute(
                    "ALTER TABLE contas_bancarias ADD COLUMN limite_credito NUMERIC(15, 2) NULL;")
                print("Coluna 'limite_credito' adicionada à tabela 'contas_bancarias'.")

    except UndefinedTable:
        print("Aviso: Alguma tabela não existe ao tentar verificar/atualizar constraints. Isso é normal se o 'create_table()' for executado primeiro.")
    except Exception as e:
        print(
            f"Erro inesperado durante a verificação/correção das constraints: {e}")
