import sqlite3
import os

# Caminho para o banco
caminho_data = r'C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Criação da tabela
with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cartoes_credito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            fechamento INTEGER NOT NULL
        )
    """)
    print("✅ Tabela cartoes_credito criada com sucesso.")