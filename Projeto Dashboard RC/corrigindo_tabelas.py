import sqlite3
import os

# Caminho para o banco de dados
caminho_data = os.path.join(os.path.dirname(__file__), "data")
caminho_banco = os.path.join(caminho_data, "dashboard_rc.db")

# Conecta e adiciona a coluna id_usuario
with sqlite3.connect(caminho_banco) as conn:
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE metas ADD COLUMN id_usuario INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Coluna 'id_usuario' adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️ A coluna 'id_usuario' já existe.")
        else:
            print(f"❌ Erro ao adicionar a coluna: {e}")