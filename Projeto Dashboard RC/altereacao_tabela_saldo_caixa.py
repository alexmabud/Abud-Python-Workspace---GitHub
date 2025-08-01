import sqlite3

# Caminho para seu banco de dados
caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

# Conecta e executa a alteração
try:
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.cursor()

        # 1. Renomeia a tabela original
        cursor.execute("ALTER TABLE saldos_caixas RENAME TO saldos_caixas_backup;")

        # 2. Cria nova tabela sem UNIQUE na data
        cursor.execute("""
            CREATE TABLE saldos_caixas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                caixa REAL DEFAULT 0.0,
                caixa_2 REAL DEFAULT 0.0,
                caixa_vendas REAL DEFAULT 0.0,
                caixa_total REAL DEFAULT 0.0,
                caixa2_dia REAL DEFAULT 0.0,
                caixa2_total REAL DEFAULT 0.0
            );
        """)

        # 3. Copia os dados da tabela antiga para a nova
        cursor.execute("""
            INSERT INTO saldos_caixas (data, caixa, caixa_2, caixa_vendas, caixa_total, caixa2_dia, caixa2_total)
            SELECT data, caixa, caixa_2, caixa_vendas, caixa_total, caixa2_dia, caixa2_total
            FROM saldos_caixas_backup;
        """)

        # 4. Remove a tabela antiga
        cursor.execute("DROP TABLE saldos_caixas_backup;")

        conn.commit()
        print("✅ Estrutura da tabela saldos_caixas atualizada com sucesso!")

except Exception as e:
    print(f"❌ Erro ao alterar a estrutura da tabela: {e}")