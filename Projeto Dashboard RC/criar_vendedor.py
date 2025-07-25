import sqlite3
import os

# Caminho correto para o banco de dados
caminho_data = os.path.join(os.path.dirname(__file__), 'data')
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Deleta tabela antiga e recria com campos esperados
with sqlite3.connect(caminho_banco) as conn:
    cursor = conn.cursor()

    # Apaga a tabela antiga se existir
    cursor.execute("DROP TABLE IF EXISTS metas")

    # Cria nova estrutura com os dias da semana e colunas de metas
    cursor.execute("""
        CREATE TABLE metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor TEXT DEFAULT 'LOJA',
            segunda REAL DEFAULT 0,
            terca REAL DEFAULT 0,
            quarta REAL DEFAULT 0,
            quinta REAL DEFAULT 0,
            sexta REAL DEFAULT 0,
            sabado REAL DEFAULT 0,
            domingo REAL DEFAULT 0,
            semanal REAL DEFAULT 0,
            mensal REAL DEFAULT 0
        );
    """)
    conn.commit()

print("✅ Tabela 'metas' recriada com sucesso!")