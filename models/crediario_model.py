from database.db_manager import execute_query


class Crediario:
    def __init__(self, id, crediario, tipo, final, limite):
        self.id = id
        self.crediario = crediario
        self.tipo = tipo
        self.final = final
        self.limite = limite

    @staticmethod
    def create_table():
        query = """
        CREATE TABLE IF NOT EXISTS crediarios (
            id SERIAL PRIMARY KEY,
            crediario VARCHAR(100) NOT NULL, 
            tipo VARCHAR(100) NOT NULL,
            final INTEGER NOT NULL,
            limite NUMERIC(10, 2) NOT NULL,
            UNIQUE(crediario, final)
        );
        """

        try:
            execute_query(query)
            print(
                "Tabela 'crediarios' verificada/criada com unicidade em (crediario, final).")
        except Exception as e:
            print(f"Erro ao criar/verificar tabela 'crediarios': {e}")

    @staticmethod
    def get_all():
        """Retorna todos os crediários do banco de dados."""
        query = "SELECT id, crediario, tipo, final, limite FROM crediarios ORDER BY crediario ASC;"
        rows = execute_query(query, fetchall=True)
        if rows:
            return [Crediario(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return []

    @staticmethod
    def get_by_id(crediario_id):
        """Retorna um crediário pelo ID."""
        query = "SELECT id, crediario, tipo, final, limite FROM crediarios WHERE id = %s;"
        row = execute_query(query, (crediario_id,), fetchone=True)
        if row:
            return Crediario(row[0], row[1], row[2], row[3], row[4])
        return None

    @staticmethod
    def add(crediario, tipo, final, limite):
        """Adiciona um novo crediário ao banco de dados."""
        query = "INSERT INTO crediarios (crediario, tipo, final, limite) VALUES (%s, %s, %s, %s) RETURNING id;"
        try:
            result = execute_query(
                query, (crediario, tipo, final, limite), fetchone=True)
            if result:
                return Crediario(result[0], crediario, tipo, final, limite)
            return None
        except Exception as e:
            # Captura exceções para informar o usuário sobre falha na inserção,
            # como violação de unicidade composta.
            print(f"Erro ao adicionar crediário: {e}")
            return None

    @staticmethod
    def update(crediario_id, crediario_val, tipo, final, limite):
        """Atualiza um crediário existente."""
        query = "UPDATE crediarios SET crediario = %s, tipo = %s, final = %s, limite = %s WHERE id = %s;"
        execute_query(query, (crediario_val, tipo,
                      final, limite, crediario_id))
        # Retorna o crediário atualizado
        return Crediario.get_by_id(crediario_id)

    @staticmethod
    def delete(crediario_id):
        """Exclui um crediário pelo ID."""
        query = "DELETE FROM crediarios WHERE id = %s;"
        execute_query(query, (crediario_id,))
        return True  # Ou verificar se a exclusão realmente ocorreu
