import sqlite3

caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fechamento_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            banco_1 REAL DEFAULT 0,
            banco_2 REAL DEFAULT 0,
            banco_3 REAL DEFAULT 0,
            banco_4 REAL DEFAULT 0,
            caixa REAL DEFAULT 0,
            caixa_2 REAL DEFAULT 0
        )
    """)
    conn.commit()

print("Tabela criada com sucesso!")