# models/contas_pagar_model.py
from database.db_manager import execute_query
from psycopg.errors import UniqueViolation


class ContasPagar:
    def __init__(self, id, conta, tipo, user_id):  # Adicionado user_id
        self.id = id
        self.conta = conta
        self.tipo = tipo
        self.user_id = user_id  # Atributo user_id

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS contas_pagar (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL, 
            conta VARCHAR(100) NOT NULL,
            tipo VARCHAR(100) NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, 
            UNIQUE(user_id, conta, tipo) 
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'contas_pagar': {e}")
            raise

    @staticmethod
    # Renomeado de get_all para get_all_for_user e adicionado user_id
    def get_all_for_user(user_id):
        """Retorna todas as contas do banco de dados para um usuário específico."""
        query = "SELECT id, conta, tipo, user_id FROM contas_pagar WHERE user_id = %s ORDER BY tipo DESC, conta ASC;"
        rows = execute_query(query, (user_id,), fetchall=True)
        if rows:
            # Passa user_id para o construtor
            return [ContasPagar(row[0], row[1], row[2], row[3]) for row in rows]
        return []

    @staticmethod
    def get_by_id(conta_id, user_id):  # Adicionado user_id
        """Retorna uma conta pelo ID e user_id."""
        query = "SELECT id, conta, tipo, user_id FROM contas_pagar WHERE id = %s AND user_id = %s;"
        row = execute_query(query, (conta_id, user_id), fetchone=True)
        if row:
            # Passa user_id para o construtor
            return ContasPagar(row[0], row[1], row[2], row[3])
        return None

    @staticmethod
    def add(conta, tipo, user_id):  # Adicionado user_id
        """Adiciona uma nova conta ao banco de dados para um usuário específico."""
        if tipo not in ('Receita', 'Despesa'):
            raise ValueError(
                "Tipo de conta inválido. Deve ser 'Receita' ou 'Despesa'.")
        # Incluído user_id no INSERT
        query = "INSERT INTO contas_pagar (conta, tipo, user_id) VALUES (%s, %s, %s) RETURNING id;"
        try:
            result = execute_query(query, (conta, tipo, user_id),  # Passa user_id para a query
                                   fetchone=True, commit=True)
            if result:
                # Passa user_id para o construtor
                return ContasPagar(result[0], conta, tipo, user_id)
            return None
        except UniqueViolation:
            # Mensagem de erro mais específica
            raise ValueError(
                f"Já existe uma conta '{conta}' do tipo '{tipo}' para este usuário.")
        except Exception as e:
            print(f"Erro ao adicionar conta: {e}")
            raise

    @staticmethod
    def update(conta_id, conta_val, tipo, user_id):  # Adicionado user_id
        """Atualiza uma conta existente para um usuário específico."""
        if tipo not in ('Receita', 'Despesa'):
            raise ValueError(
                "Tipo de conta inválido. Deve ser 'Receita' ou 'Despesa'.")
        # Incluído user_id no WHERE
        query = "UPDATE contas_pagar SET conta = %s, tipo = %s WHERE id = %s AND user_id = %s;"
        try:
            execute_query(query, (conta_val, tipo, conta_id, user_id),
                          commit=True)  # Passa user_id para a query
            # Busca usando user_id
            return ContasPagar.get_by_id(conta_id, user_id)
        except UniqueViolation:
            # Mensagem de erro mais específica
            raise ValueError(
                f"Já existe outra conta '{conta_val}' do tipo '{tipo}' para este usuário.")
        except Exception as e:
            print(f"Erro ao atualizar conta: {e}")
            raise

    @staticmethod
    def delete(conta_id, user_id):  # Adicionado user_id
        """Exclui uma conta pelo ID e user_id."""
        query = "DELETE FROM contas_pagar WHERE id = %s AND user_id = %s;"  # Incluído user_id no WHERE
        # Passa user_id para a query
        execute_query(query, (conta_id, user_id), commit=True)
        return True
