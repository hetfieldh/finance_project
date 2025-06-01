
from database.db_manager import execute_query


class ContasPagar:
    def __init__(self, id, conta, tipo):
        self.id = id
        self.conta = conta
        self.tipo = tipo

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS contas_pagar (
            id SERIAL PRIMARY KEY,
            conta VARCHAR(100) NOT NULL,
            tipo VARCHAR(100) NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
            UNIQUE(conta, tipo)
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'contas_pagar': {e}")
            raise

    @staticmethod
    def get_all():
        """Retorna todas as contas do banco de dados."""
        query = "SELECT id, conta, tipo FROM contas_pagar ORDER BY tipo DESC, conta ASC;"
        rows = execute_query(query, fetchall=True)
        if rows:
            return [ContasPagar(row[0], row[1], row[2]) for row in rows]
        return []

    @staticmethod
    def get_by_id(conta_id):
        """Retorna uma conta pelo ID."""
        query = "SELECT id, conta, tipo FROM contas_pagar WHERE id = %s;"
        row = execute_query(query, (conta_id,), fetchone=True)
        if row:
            return ContasPagar(row[0], row[1], row[2])
        return None

    @staticmethod
    def add(conta, tipo):
        """Adiciona uma nova conta ao banco de dados."""
        if tipo not in ('Receita', 'Despesa'):
            raise ValueError(
                "Tipo de conta inválido. Deve ser 'Receita' ou 'Despesa'.")
        query = "INSERT INTO contas_pagar (conta, tipo) VALUES (%s, %s) RETURNING id;"
        result = execute_query(query, (conta, tipo),
                               fetchone=True, commit=True)
        if result:
            return ContasPagar(result[0], conta, tipo)
        return None

    @staticmethod
    def update(conta_id, conta, tipo):
        """Atualiza uma conta existente."""
        if tipo not in ('Receita', 'Despesa'):
            raise ValueError(
                "Tipo de conta inválido. Deve ser 'Receita' ou 'Despesa'.")
        query = "UPDATE contas_pagar SET conta = %s, tipo = %s WHERE id = %s;"
        execute_query(query, (conta, tipo, conta_id), commit=True)
        return ContasPagar.get_by_id(conta_id)

    @staticmethod
    def delete(conta_id):
        """Exclui uma conta pelo ID."""
        query = "DELETE FROM contas_pagar WHERE id = %s;"
        execute_query(query, (conta_id,), commit=True)
        return True
