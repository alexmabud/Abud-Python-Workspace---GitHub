import sqlite3
import pandas as pd
import os

CAMINHO = "data/entrada.db"

# Verifica se o arquivo existe
if not os.path.exists(CAMINHO):
    print("🚫 Banco de dados 'entrada.db' NÃO encontrado na pasta 'data/'.")
else:
    print("✅ Banco de dados encontrado!")

    conexao = sqlite3.connect(CAMINHO)
    cursor = conexao.cursor()

    # Verifica as tabelas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = [t[0] for t in cursor.fetchall()]
    print(f"\n📋 Tabelas encontradas no banco: {tabelas}\n")

    # Mostra os 5 primeiros registros de cada tabela
    for tabela in tabelas:
        print(f"🔎 Primeiros registros da tabela: {tabela}")
        try:
            df = pd.read_sql(f"SELECT * FROM {tabela} ORDER BY data LIMIT 5", conexao)
            print(df)
        except Exception as e:
            print(f"Erro ao ler tabela {tabela}: {e}")
        print("\n" + "-"*50 + "\n")

    conexao.close()