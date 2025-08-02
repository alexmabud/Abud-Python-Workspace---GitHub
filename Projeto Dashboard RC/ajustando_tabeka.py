import sqlite3
import os

# Caminho do banco de dados (ajuste conforme necessário)
caminho_banco = os.path.join(
    "C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data",
    "dashboard_rc.db"
)

# Conectar ao banco
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

try:
    # 1. Renomear a tabela antiga
    cursor.execute("ALTER TABLE taxas_maquinas RENAME TO taxas_maquinas_old;")

    # 2. Criar nova tabela com a coluna 'maquineta'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS taxas_maquinas (
        maquineta TEXT NOT NULL,
        forma_pagamento TEXT NOT NULL,
        bandeira TEXT NOT NULL,
        parcelas INTEGER NOT NULL,
        taxa_percentual REAL NOT NULL,
        PRIMARY KEY (maquineta, forma_pagamento, bandeira, parcelas)
    );
    """)

    # 3. Migrar os dados antigos com 'CIELO' como valor da nova coluna
    cursor.execute("""
    INSERT INTO taxas_maquinas (maquineta, forma_pagamento, bandeira, parcelas, taxa_percentual)
    SELECT 'CIELO', forma_pagamento, bandeira, parcelas, taxa_percentual
    FROM taxas_maquinas_old;
    """)

    # 4. Remover a tabela antiga
    cursor.execute("DROP TABLE taxas_maquinas_old;")

    conn.commit()
    print("✅ Tabela 'taxas_maquinas' atualizada com sucesso com a coluna 'maquineta' preenchida como 'CIELO'.")

except Exception as e:
    print("❌ Ocorreu um erro ao atualizar a tabela:", e)

finally:
    conn.close()