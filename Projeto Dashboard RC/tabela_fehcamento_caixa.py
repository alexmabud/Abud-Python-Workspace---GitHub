import sqlite3
import os

# Caminho do banco (ajuste se estiver diferente)
caminho_data = r'C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Conecta e cria a tabela
with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fechamento_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            banco_1 REAL,
            banco_2 REAL,
            banco_3 REAL,
            banco_4 REAL,
            caixa REAL,
            caixa_2 REAL,
            entradas_confirmadas REAL,
            saidas REAL,
            correcao REAL,
            saldo_esperado REAL,
            valor_informado REAL,
            diferenca REAL
        );
    """)
    conn.commit()

print("✅ Tabela 'fechamento_caixa' criada com sucesso!")