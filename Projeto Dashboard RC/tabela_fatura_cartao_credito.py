import sqlite3

# Caminho para o banco de dados
caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

# Criação da tabela fatura_cartao se não existir
with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fatura_cartao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            vencimento TEXT,
            cartao TEXT,
            parcela INTEGER,
            total_parcelas INTEGER,
            valor REAL,
            categoria TEXT,
            sub_categoria TEXT,
            descricao TEXT,
            usuario TEXT
        )
    """)
    conn.commit()

print("✅ Tabela 'fatura_cartao' criada (ou já existia).")