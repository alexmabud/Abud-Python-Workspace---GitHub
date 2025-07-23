import sqlite3
import os

# Caminho do banco de dados (ajuste conforme seu ambiente)
caminho_data = r'C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Conectar ao banco e criar as tabelas
with sqlite3.connect(caminho_banco) as conn:
    # Tabela de Compras
    conn.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            valor REAL,
            forma_pagamento TEXT,
            parcela INTEGER,
            categoria TEXT,
            subcategoria TEXT,
            descricao TEXT
        )
    """)

    # Tabela de Contas a Pagar
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contas_a_pagar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            descricao TEXT
        )
    """)

print("✅ Tabelas 'compras' e 'contas_a_pagar' criadas com sucesso!")