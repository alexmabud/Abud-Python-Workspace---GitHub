import sqlite3

# Altere o caminho abaixo conforme seu projeto
caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

with sqlite3.connect(caminho_banco) as conn:
    cursor = conn.cursor()

    # Verifica as colunas atuais da tabela
    colunas_atuais = [col[1] for col in cursor.execute("PRAGMA table_info(saida)").fetchall()]

    # Cria Origem_Dinheiro se ainda não existir
    if "Origem_Dinheiro" not in colunas_atuais:
        cursor.execute("ALTER TABLE saida ADD COLUMN Origem_Dinheiro TEXT")
        print("✅ Coluna 'Origem_Dinheiro' adicionada.")

    # Cria Banco_Saida se ainda não existir
    if "Banco_Saida" not in colunas_atuais:
        cursor.execute("ALTER TABLE saida ADD COLUMN Banco_Saida TEXT")
        print("✅ Coluna 'Banco_Saida' adicionada.")

    conn.commit()