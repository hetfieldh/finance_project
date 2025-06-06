from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from database.db_manager import execute_query
from psycopg.errors import UniqueViolation


class MovimentoCrediario:
    def __init__(self, id, data_compra, descricao, id_grupo_crediario, id_crediario, valor_total, num_parcelas, primeira_parcela, user_id, ultima_parcela=None, valor_parcela_mensal=None):
        self.id = id
        self.data_compra = data_compra
        self.descricao = descricao
        self.id_grupo_crediario = id_grupo_crediario
        self.id_crediario = id_crediario
        self.valor_total = float(valor_total)
        self.num_parcelas = int(num_parcelas)
        self.primeira_parcela = primeira_parcela
        self.ultima_parcela = ultima_parcela if ultima_parcela else self._calculate_ultima_parcela()
        self.valor_parcela_mensal = valor_parcela_mensal if valor_parcela_mensal else self._calculate_valor_parcela_mensal()
        self.user_id = user_id

    def _calculate_ultima_parcela(self):
        """Calcula a data da última parcela com base na primeira parcela e número de parcelas."""
        if not self.primeira_parcela or not self.num_parcelas or self.num_parcelas == 0:
            return None
        return self.primeira_parcela + relativedelta(months=self.num_parcelas - 1)

    def _calculate_valor_parcela_mensal(self):
        """Calcula o valor da parcela mensal."""
        if not self.valor_total or not self.num_parcelas or self.num_parcelas == 0:
            return 0.0
        return round(self.valor_total / self.num_parcelas, 2)

    @staticmethod
    def create_table():
        """Cria a tabela 'movimento_crediario' se ela não existir."""
        query = """
        CREATE TABLE IF NOT EXISTS movimento_crediario (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            data_compra DATE NOT NULL,
            descricao VARCHAR(255) NOT NULL,
            id_grupo_crediario INTEGER NOT NULL,
            id_crediario INTEGER NOT NULL,
            valor_total DECIMAL(10, 2) NOT NULL,
            num_parcelas INTEGER NOT NULL,
            primeira_parcela DATE NOT NULL,
            ultima_parcela DATE NOT NULL,
            valor_parcela_mensal DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (id_grupo_crediario) REFERENCES grupo_crediario(id) ON DELETE RESTRICT,
            FOREIGN KEY (id_crediario) REFERENCES crediarios(id) ON DELETE RESTRICT
        );
        """
        try:
            execute_query(query, commit=True)
        except Exception as e:
            print(
                f"ERRO CRÍTICO ao criar/verificar tabela 'movimento_crediario': {e}")
            raise

    @staticmethod
    def get_all_for_user(user_id):
        """Retorna todos os movimentos de crediário para um usuário específico, com nomes de grupo e crediário."""
        query = """
        SELECT
            mc.id,
            mc.data_compra,
            mc.descricao,
            mc.id_grupo_crediario,
            gc.grupo AS nome_grupo_crediario,
            mc.id_crediario,
            c.crediario AS nome_crediario,
            mc.valor_total,
            mc.num_parcelas,
            mc.primeira_parcela,
            mc.ultima_parcela,
            mc.valor_parcela_mensal,
            mc.user_id
        FROM
            movimento_crediario mc
        JOIN
            grupo_crediario gc ON mc.id_grupo_crediario = gc.id
        JOIN
            crediarios c ON mc.id_crediario = c.id
        WHERE
            mc.user_id = %s
        ORDER BY
            mc.data_compra DESC;
        """
        rows = execute_query(query, (user_id,), fetchall=True)
        if rows:
            # O construtor espera o user_id na posição 8 (última), mas o select retorna 13 colunas
            # Precisamos ajustar para retornar os dados corretamente no construtor e adicionar os nomes
            # Podemos criar uma subclasse ou um dicionário para facilitar
            movimentos = []
            for row in rows:
                # Criar um objeto temporário ou dicionário para passar para o template
                # Vamos estender o MovimentoCrediario para incluir os nomes para o template
                mov = MovimentoCrediario(
                    id=row[0],
                    data_compra=row[1],
                    descricao=row[2],
                    id_grupo_crediario=row[3],
                    id_crediario=row[5],
                    valor_total=row[7],
                    num_parcelas=row[8],
                    primeira_parcela=row[9],
                    ultima_parcela=row[10],
                    valor_parcela_mensal=row[11],
                    user_id=row[12]
                )
                # Adiciona o nome do grupo como atributo extra
                mov.nome_grupo_crediario = row[4]
                # Adiciona o nome do crediário como atributo extra
                mov.nome_crediario = row[6]
                movimentos.append(mov)
            return movimentos
        return []

    @staticmethod
    def get_by_id(movimento_id, user_id):
        """Retorna um movimento de crediário pelo ID e pelo user_id."""
        query = """
        SELECT
            mc.id,
            mc.data_compra,
            mc.descricao,
            mc.id_grupo_crediario,
            gc.grupo AS nome_grupo_crediario,
            mc.id_crediario,
            c.crediario AS nome_crediario,
            mc.valor_total,
            mc.num_parcelas,
            mc.primeira_parcela,
            mc.ultima_parcela,
            mc.valor_parcela_mensal,
            mc.user_id
        FROM
            movimento_crediario mc
        JOIN
            grupo_crediario gc ON mc.id_grupo_crediario = gc.id
        JOIN
            crediarios c ON mc.id_crediario = c.id
        WHERE
            mc.id = %s AND mc.user_id = %s;
        """
        row = execute_query(query, (movimento_id, user_id), fetchone=True)
        if row:
            mov = MovimentoCrediario(
                id=row[0],
                data_compra=row[1],
                descricao=row[2],
                id_grupo_crediario=row[3],
                id_crediario=row[5],
                valor_total=row[7],
                num_parcelas=row[8],
                primeira_parcela=row[9],
                ultima_parcela=row[10],
                valor_parcela_mensal=row[11],
                user_id=row[12]
            )
            mov.nome_grupo_crediario = row[4]
            mov.nome_crediario = row[6]
            return mov
        return None

    @staticmethod
    def add(data_compra, descricao, id_grupo_crediario, id_crediario, valor_total, num_parcelas, primeira_parcela, user_id):
        """Adiciona um novo movimento de crediário."""
        # Cria um objeto temporário para calcular ultima_parcela e valor_parcela_mensal
        temp_mov = MovimentoCrediario(
            id=None,  # ID é None pois ainda não foi inserido
            data_compra=data_compra,
            descricao=descricao,
            id_grupo_crediario=id_grupo_crediario,
            id_crediario=id_crediario,
            valor_total=valor_total,
            num_parcelas=num_parcelas,
            primeira_parcela=primeira_parcela,
            user_id=user_id
        )

        ultima_parcela = temp_mov.ultima_parcela
        valor_parcela_mensal = temp_mov.valor_parcela_mensal

        query = """
        INSERT INTO movimento_crediario (
            data_compra, descricao, id_grupo_crediario, id_crediario,
            valor_total, num_parcelas, primeira_parcela, ultima_parcela,
            valor_parcela_mensal, user_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        try:
            result = execute_query(
                query,
                (data_compra, descricao, id_grupo_crediario, id_crediario,
                 valor_total, num_parcelas, primeira_parcela, ultima_parcela,
                 valor_parcela_mensal, user_id),
                fetchone=True,
                commit=True
            )
            if result:
                return MovimentoCrediario(result[0], data_compra, descricao, id_grupo_crediario, id_crediario,
                                          valor_total, num_parcelas, primeira_parcela, user_id,
                                          ultima_parcela, valor_parcela_mensal)
            return None
        except Exception as e:
            print(f"Erro ao adicionar movimento de crediário: {e}")
            raise

    @staticmethod
    def update(movimento_id, data_compra, descricao, id_grupo_crediario, id_crediario, valor_total, num_parcelas, primeira_parcela, user_id):
        """Atualiza um movimento de crediário existente."""
        # Cria um objeto temporário para recalcular ultima_parcela e valor_parcela_mensal
        temp_mov = MovimentoCrediario(
            id=movimento_id,
            data_compra=data_compra,
            descricao=descricao,
            id_grupo_crediario=id_grupo_crediario,
            id_crediario=id_crediario,
            valor_total=valor_total,
            num_parcelas=num_parcelas,
            primeira_parcela=primeira_parcela,
            user_id=user_id
        )

        ultima_parcela = temp_mov.ultima_parcela
        valor_parcela_mensal = temp_mov.valor_parcela_mensal

        query = """
        UPDATE movimento_crediario SET
            data_compra = %s,
            descricao = %s,
            id_grupo_crediario = %s,
            id_crediario = %s,
            valor_total = %s,
            num_parcelas = %s,
            primeira_parcela = %s,
            ultima_parcela = %s,
            valor_parcela_mensal = %s
        WHERE id = %s AND user_id = %s;
        """
        try:
            execute_query(
                query,
                (data_compra, descricao, id_grupo_crediario, id_crediario,
                 valor_total, num_parcelas, primeira_parcela, ultima_parcela,
                 valor_parcela_mensal, movimento_id, user_id),
                commit=True
            )
            return MovimentoCrediario.get_by_id(movimento_id, user_id)
        except Exception as e:
            print(f"Erro ao atualizar movimento de crediário: {e}")
            raise

    @staticmethod
    def delete(movimento_id, user_id):
        """Exclui um movimento de crediário pelo ID e pelo user_id."""
        query = "DELETE FROM movimento_crediario WHERE id = %s AND user_id = %s;"
        execute_query(query, (movimento_id, user_id), commit=True)
        return True

    @staticmethod
    def get_parcelas_mensais_por_mes(user_id, ano, mes):
        """
        Calcula o valor total das parcelas de crediário a serem pagas em um determinado mês/ano.
        Retorna a soma das parcelas de movimentos ativos no mês de referência.
        """
        # Consideramos parcelas que:
        # 1. Começaram antes ou no mês de referência E
        # 2. Terminarão no mês de referência ou depois
        # 3. O valor total é dividido pelo número de parcelas para obter o valor mensal
        # Note: Esta é uma simplificação. Se você tiver juros ou amortização complexa,
        # precisará de uma lógica financeira mais robusta (ex: tabela de amortização).
        # Aqui, estamos assumindo que cada parcela é ValorTotal / NumParcelas.

        # Filtra os movimentos cujas parcelas se estendem até o mês de referência
        query = """
        SELECT
            SUM(valor_parcela_mensal)
        FROM
            movimento_crediario
        WHERE
            user_id = %s AND
            primeira_parcela <= %s AND
            ultima_parcela >= %s;
        """
        # Para primeira_parcela <= 'YYYY-MM-DD'
        # Para ultima_parcela >= 'YYYY-MM-DD'
        # O ideal é pegar o último dia do mês para primeira_parcela e o primeiro dia do mês para ultima_parcela

        # O primeiro dia do mês de referência
        start_of_month = date(ano, mes, 1)

        # O último dia do mês de referência
        if mes == 12:
            end_of_month = date(ano, mes, 31)
        else:
            end_of_month = date(ano, mes + 1, 1) - timedelta(days=1)

        result = execute_query(
            query, (user_id, end_of_month, start_of_month), fetchone=True)

        return result[0] if result and result[0] is not None else 0.0
