import sqlite3

# Caminho do seu banco de dados
caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

# Criação da tabela saldos_caixas
with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saldos_caixas (
            data TEXT PRIMARY KEY,
            caixa REAL DEFAULT 0.0,
            caixa_2 REAL DEFAULT 0.0
        );
    """)
    conn.commit()

print("✅ Tabela 'saldos_caixas' criada com sucesso.")