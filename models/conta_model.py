from database.db_manager import execute_query


class Conta:
    def __init__(self, id, nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite):
        self.id = id
        self.nome_banco = nome_banco
        self.agencia = agencia
        self.numero_conta = numero_conta
        self.tipo = tipo
        self.saldo_inicial = saldo_inicial
        self.limite = limite

    @staticmethod
    def create_table():
        """Cria a tabela contas se ela não existir, com unicidade em (agencia, numero_conta, tipo)."""
        query = """
        CREATE TABLE IF NOT EXISTS contas (
            id SERIAL PRIMARY KEY,
            nome_banco VARCHAR(100) NOT NULL,
            agencia INTEGER NOT NULL,
            numero_conta BIGINT NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            saldo_inicial NUMERIC(15, 2) NOT NULL,
            limite NUMERIC(15, 2) NOT NULL,
            UNIQUE(agencia, numero_conta, tipo)
        );
        """
        try:
            execute_query(query)
            print(
                "Tabela 'contas' verificada/criada com unicidade em (agencia, numero_conta, tipo).")
        except Exception as e:
            print(f"Erro ao criar/verificar tabela 'contas': {e}")

    @staticmethod
    def get_all():
        """Retorna todas as contas do banco de dados."""
        query = "SELECT id, nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite FROM contas ORDER BY nome_banco ASC, tipo ASC;"
        rows = execute_query(query, fetchall=True)
        if rows:
            return [Conta(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]
        return []

    @staticmethod
    def get_by_id(conta_id):
        """Retorna uma conta pelo ID."""
        query = "SELECT id, nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite FROM contas WHERE id = %s;"
        row = execute_query(query, (conta_id,), fetchone=True)
        if row:
            return Conta(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        return None

    @staticmethod
    def add(nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite):
        """Adiciona uma nova conta ao banco de dados."""
        query = """
        INSERT INTO contas (nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        result = execute_query(
            query, (nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite), fetchone=True)
        if result:
            return Conta(result[0], nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite)
        return None

    @staticmethod
    def update(conta_id, nome_banco, agencia, numero_conta, tipo, saldo_inicial, limite):
        """Atualiza uma conta existente."""
        query = """
        UPDATE contas SET
        nome_banco = %s, agencia = %s, numero_conta = %s, tipo = %s, saldo_inicial = %s, limite = %s
        WHERE id = %s;
        """
        execute_query(query, (nome_banco, agencia, numero_conta,
                      tipo, saldo_inicial, limite, conta_id))
        return Conta.get_by_id(conta_id)

    @staticmethod
    def delete(conta_id):
        """Exclui uma conta pelo ID."""
        query = "DELETE FROM contas WHERE id = %s;"
        execute_query(query, (conta_id,))
        return True
