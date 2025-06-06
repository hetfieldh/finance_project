# database/bd_manager.py
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
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'password_hash';
            """)
            if not cursor.fetchone():
                print("Adicionando coluna 'password_hash' à tabela 'users'...")
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);")
                print("Coluna 'password_hash' adicionada à tabela 'users'.")

            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'is_active';
            """)
            if not cursor.fetchone():
                print("Adicionando coluna 'is_active' à tabela 'users'...")
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
                print("Coluna 'is_active' adicionada à tabela 'users'.")

            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'is_admin';
            """)
            if not cursor.fetchone():
                print("Adicionando coluna 'is_admin' à tabela 'users'...")
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;")
                print("Coluna 'is_admin' adicionada à tabela 'users'.")

            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'contas_bancarias' AND column_name = 'saldo_atual';
            """)
            if not cursor.fetchone():
                print("Adicionando coluna 'saldo_atual' à tabela 'contas_bancarias'...")
                cursor.execute(
                    "ALTER TABLE contas_bancarias ADD COLUMN NUMERIC(15, 2) NOT NULL DEFAULT 0.0;")
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

            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'tipos_crediario'
                );
            """)
            if cursor.fetchone()[0]:
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'tipos_crediario' AND column_name = 'user_id';
                """)
                if not cursor.fetchone():
                    print("Adicionando coluna 'user_id' à tabela 'tipos_crediario'...")
                    cursor.execute(
                        "ALTER TABLE tipos_crediario ADD COLUMN user_id INTEGER;")
                    cursor.execute(
                        "ALTER TABLE tipos_crediario ADD CONSTRAINT fk_user_id_tipos_crediario FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;")
                    print(
                        "Coluna 'user_id' e FK adicionadas à tabela 'tipos_crediario'.")

                cursor.execute("""
                    SELECT conname FROM pg_constraint
                    WHERE conrelid = 'public.tipos_crediario'::regclass AND contype = 'u' AND conkey = ARRAY[
                        (SELECT attnum FROM pg_attribute WHERE attrelid = 'public.tipos_crediario'::regclass AND attname = 'user_id'),
                        (SELECT attnum FROM pg_attribute WHERE attrelid = 'public.tipos_crediario'::regclass AND attname = 'nome_tipo')
                    ];
                """)
                if not cursor.fetchone():
                    print(
                        "Adicionando UNIQUE constraint (user_id, nome_tipo) à tabela 'tipos_crediario'...")
                    cursor.execute(
                        "ALTER TABLE tipos_crediario ADD CONSTRAINT unique_user_tipo UNIQUE (user_id, nome_tipo);")
                    print("UNIQUE constraint adicionada à tabela 'tipos_crediario'.")

    except UndefinedTable:
        print("Aviso: Alguma tabela não existe ao tentar verificar/atualizar constraints. Isso é normal se o 'create_table()' for executado primeiro.")
    except Exception as e:
        print(
            f"Erro inesperado durante a verificação/correção das constraints: {e}")
