import sqlite3
import os

# Caminho do banco de dados
caminho_data = r'C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Criação da tabela de correção de caixa
with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS correcao_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            observacao TEXT
        )
    """)

print("✅ Tabela 'correcao_caixa' criada com sucesso!")