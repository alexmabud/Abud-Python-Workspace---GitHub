import sqlite3
import os

# Caminho do banco (ajustado conforme seu projeto)
caminho_data = r'C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Conectar
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

# 1. Copiar os dados existentes
cursor.execute("SELECT forma_pagamento, bandeira, parcelas, taxa_percentual FROM taxas_maquinas")
dados_antigos = cursor.fetchall()

# 2. Apagar a tabela antiga
cursor.execute("DROP TABLE IF EXISTS taxas_maquinas")

# 3. Criar nova tabela com chave primária composta
cursor.execute("""
    CREATE TABLE taxas_maquinas (
        forma_pagamento TEXT NOT NULL,
        bandeira TEXT NOT NULL,
        parcelas INTEGER NOT NULL,
        taxa_percentual REAL NOT NULL,
        PRIMARY KEY (forma_pagamento, bandeira, parcelas)
    )
""")

# 4. Inserir os dados de volta (sem duplicatas)
ja_inseridos = set()
for fp, bandeira, parcelas, taxa in dados_antigos:
    chave = (fp.upper(), bandeira.upper(), parcelas)
    if chave not in ja_inseridos:
        cursor.execute("""
            INSERT INTO taxas_maquinas (forma_pagamento, bandeira, parcelas, taxa_percentual)
            VALUES (?, ?, ?, ?)
        """, chave + (taxa,))
        ja_inseridos.add(chave)

# Finalizar
conn.commit()
conn.close()

print("✅ Tabela 'taxas_maquinas' recriada com chave primária e dados restaurados.")