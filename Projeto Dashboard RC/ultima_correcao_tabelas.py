import sqlite3
import os

# Caminho do banco
caminho_banco = os.path.join(
    "C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data",
    "dashboard_rc.db"
)

conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

try:
    # 1. Renomear tabela original
    cursor.execute("ALTER TABLE entrada RENAME TO entrada_old;")

    # 2. Criar nova tabela com tipos corrigidos
    cursor.execute("""
        CREATE TABLE entrada (
            Data TEXT,
            Valor REAL,
            Forma_de_Pagamento TEXT,
            Parcelas REAL,
            Bandeira TEXT,
            Usuario TEXT,
            maquineta TEXT,
            valor_liquido REAL
        );
    """)

    # 3. Migrar os dados convertendo `Forma_de_Pagamento` e `Bandeira` para TEXT
    cursor.execute("""
        INSERT INTO entrada (
            Data, Valor, Forma_de_Pagamento, Parcelas, Bandeira, Usuario, maquineta, valor_liquido
        )
        SELECT
            Data,
            Valor,
            CAST(Forma_de_Pagamento AS TEXT),
            Parcelas,
            CAST(Bandeira AS TEXT),
            Usuario,
            maquineta,
            valor_liquido
        FROM entrada_old;
    """)

    # 4. Apagar a tabela antiga
    cursor.execute("DROP TABLE entrada_old;")

    conn.commit()
    print("✅ Tabela 'entrada' corrigida com sucesso (Forma_de_Pagamento e Bandeira agora são TEXT).")

except Exception as e:
    print("❌ Erro ao corrigir a tabela 'entrada':", e)

finally:
    conn.close()