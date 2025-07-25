import sqlite3
import os

# Caminho até o banco de dados
caminho_data = os.path.join(os.path.dirname(__file__), 'data')
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Adiciona a coluna 'Usuario' na tabela 'entrada', se ainda não existir
try:
    with sqlite3.connect(caminho_banco) as conn:
        conn.execute("ALTER TABLE entrada ADD COLUMN Usuario TEXT;")
        conn.commit()
    print("✅ Coluna 'Usuario' adicionada com sucesso.")
except Exception as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️ A coluna 'Usuario' já existe.")
    else:
        print(f"❌ Erro ao adicionar coluna: {e}")