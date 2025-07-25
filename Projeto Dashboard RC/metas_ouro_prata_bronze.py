import sqlite3

# Caminho do seu banco de dados
caminho_banco = r'C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db'

# Conectar ao banco
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

# Verifica se as colunas já existem
cursor.execute("PRAGMA table_info(metas)")
colunas_existentes = [col[1] for col in cursor.fetchall()]

# Cria as colunas apenas se não existirem
if "meta_ouro" not in colunas_existentes:
    cursor.execute("ALTER TABLE metas ADD COLUMN meta_ouro REAL DEFAULT 0")
    print("Coluna 'meta_ouro' adicionada.")

if "meta_prata" not in colunas_existentes:
    cursor.execute("ALTER TABLE metas ADD COLUMN meta_prata REAL DEFAULT 0")
    print("Coluna 'meta_prata' adicionada.")

if "meta_bronze" not in colunas_existentes:
    cursor.execute("ALTER TABLE metas ADD COLUMN meta_bronze REAL DEFAULT 0")
    print("Coluna 'meta_bronze' adicionada.")

# Salva e fecha
conn.commit()
conn.close()

print("✅ Atualização concluída com sucesso!")