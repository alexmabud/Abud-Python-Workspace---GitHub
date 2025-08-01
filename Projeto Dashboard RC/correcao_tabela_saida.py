import sqlite3

caminho_banco = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db"

with sqlite3.connect(caminho_banco) as conn:
    cursor = conn.cursor()

    # 1. Renomeia a tabela original
    cursor.execute("ALTER TABLE saida RENAME TO saida_antiga")

    # 2. Cria a nova tabela com os tipos corretos
    cursor.execute("""
        CREATE TABLE saida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Data TEXT,
            Valor REAL,
            Forma_de_Pagamento TEXT,
            Parcelas INTEGER,
            Categoria TEXT,
            Sub_Categoria TEXT,
            Descricao TEXT,
            Usuario TEXT
        )
    """)

    # 3. Copia os dados da antiga para a nova tabela
    cursor.execute("""
        INSERT INTO saida (Data, Valor, Forma_de_Pagamento, Parcelas, Categoria, Sub_Categoria, Descricao, Usuario)
        SELECT Data, Valor, Forma_de_Pagamento, CAST(Parcelas AS INTEGER), Categoria, Sub_Categoria, Descricao, Usuario
        FROM saida_antiga
    """)

    # 4. Exclui a tabela antiga
    cursor.execute("DROP TABLE saida_antiga")

    conn.commit()
    print("✅ Tabela 'saida' corrigida com sucesso.")