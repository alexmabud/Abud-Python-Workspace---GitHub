import sqlite3
import os

# Caminho do banco de dados
caminho_banco = os.path.join(
    "C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data",
    "dashboard_rc.db"
)

# Conectar ao banco
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

# Verifica as colunas existentes
cursor.execute("PRAGMA table_info(entrada);")
colunas = [col[1] for col in cursor.fetchall()]

# Adicionar coluna 'maquineta' se não existir
if "maquineta" not in colunas:
    cursor.execute("ALTER TABLE entrada ADD COLUMN maquineta TEXT;")
    print("✅ Coluna 'maquineta' adicionada à tabela 'entrada'.")

# Adicionar coluna 'valor_liquido' se não existir
if "valor_liquido" not in colunas:
    cursor.execute("ALTER TABLE entrada ADD COLUMN valor_liquido REAL;")
    print("✅ Coluna 'valor_liquido' adicionada à tabela 'entrada'.")

conn.commit()
conn.close()