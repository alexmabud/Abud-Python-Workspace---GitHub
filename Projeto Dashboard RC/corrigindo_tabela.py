import sqlite3
import os

# Caminho do banco de dados (ajustado ao seu projeto)
caminho_banco = os.path.join(
    "C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data",
    "dashboard_rc.db"
)

# Conectar ao banco
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

# 1. Renomear a tabela atual
cursor.execute("ALTER TABLE taxas_maquinas RENAME TO taxas_maquinas_old;")

# 2. Criar nova tabela com coluna 'maquineta' incluída
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

# 3. Migrar dados antigos com valor 'PADRAO' como maquineta
cursor.execute("""
INSERT INTO taxas_maquinas (maquineta, forma_pagamento, bandeira, parcelas, taxa_percentual)
SELECT 'PADRAO', forma_pagamento, bandeira, parcelas, taxa_percentual
FROM taxas_maquinas_old;
""")

# 4. Excluir tabela antiga (opcional, após migração bem-sucedida)
cursor.execute("DROP TABLE taxas_maquinas_old;")

# Finalizar
conn.commit()
conn.close()

print("✅ Tabela 'taxas_maquinas' atualizada com sucesso com a coluna 'maquineta'.")