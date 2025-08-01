import sqlite3

# Caminho completo para o seu banco de dados
caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

# Conecta ao banco e verifica se a coluna 'Usuario' existe na tabela 'saida'
with sqlite3.connect(caminho_banco) as conn:
    colunas_saida = conn.execute("PRAGMA table_info(saida)").fetchall()
    nomes_colunas = [col[1] for col in colunas_saida]

    if "Usuario" not in nomes_colunas:
        conn.execute("ALTER TABLE saida ADD COLUMN Usuario TEXT;")
        print("✅ Coluna 'Usuario' adicionada com sucesso à tabela 'saida'.")
    else:
        print("ℹ️ A coluna 'Usuario' já existe na tabela 'saida'. Nenhuma alteração foi feita.")