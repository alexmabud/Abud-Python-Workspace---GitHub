import sqlite3

# Caminho correto do seu banco de dados
caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

# Criar a tabela saldos_bancos com os quatro bancos
with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saldos_bancos (
            data TEXT PRIMARY KEY,
            banco_1 REAL DEFAULT 0.0,
            banco_2 REAL DEFAULT 0.0,
            banco_3 REAL DEFAULT 0.0,
            banco_4 REAL DEFAULT 0.0
        )
    """)
    conn.commit()

print("✅ Tabela 'saldos_bancos' criada com sucesso!")