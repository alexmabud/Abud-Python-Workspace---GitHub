import sqlite3

caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

with sqlite3.connect(caminho_banco) as conn:
    # Verifica se a coluna 'vencimento' já existe
    colunas = [info[1] for info in conn.execute("PRAGMA table_info(cartoes_credito)").fetchall()]
    
    if "vencimento" not in colunas:
        # Adiciona a nova coluna
        conn.execute("ALTER TABLE cartoes_credito ADD COLUMN vencimento INTEGER")
        print("✅ Coluna 'vencimento' adicionada com sucesso.")

        # Preenche com o mesmo valor da coluna 'fechamento'
        conn.execute("UPDATE cartoes_credito SET vencimento = fechamento")
        print("✅ Coluna 'vencimento' preenchida com base na coluna 'fechamento'.")
    else:
        print("ℹ️ A coluna 'vencimento' já existe.")
    
    conn.commit()