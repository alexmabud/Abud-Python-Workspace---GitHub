import os
import sqlite3
import pandas as pd

# Garante que a pasta 'data' existe
os.makedirs("data", exist_ok=True)

# Caminho do banco SQLite (o mesmo de entradas)
caminho_banco = "data/entrada.db"

# === CRIA A TABELA DE SAÍDAS ===
print("🔧 Criando tabela 'saidas' no banco...")
conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS saidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    valor REAL,
    categoria TEXT,
    descricao TEXT
)
''')
conexao.commit()
conexao.close()
print("✅ Tabela 'saidas' criada ou já existente.\n")

# === FUNÇÃO PARA INSERIR REGISTROS ===
def inserir_saidas(lista):
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()
    for item in lista:
        cursor.execute('''
            INSERT INTO saidas (data, valor, categoria, descricao)
            VALUES (?, ?, ?, ?)
        ''', (
            item["data"],
            item["valor"],
            item["categoria"],
            item["descricao"]
        ))
    conexao.commit()
    conexao.close()

# === FUNÇÃO PARA TRATAR E IMPORTAR ARQUIVOS DE SAÍDAS ===
def tratar_saida(arquivo, ano):
    print(f"📥 Importando saídas de {ano}...")
    df = pd.read_excel(arquivo, header=None)  # força leitura sem cabeçalho
    colunas = ["data"] + [f"col_{i}" for i in range(1, df.shape[1])]
    df.columns = colunas

    df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")

    registros = []
    for _, row in df.iterrows():
        data = row["data"]
        for col in df.columns:
            if col != "data":
                valor = pd.to_numeric(row.get(col), errors="coerce")
                if pd.notnull(valor) and valor > 0:
                    registros.append({
                        "data": data,
                        "valor": float(valor),
                        "categoria": "Saída Geral",
                        "descricao": "Consolidado do dia"
                    })

    inserir_saidas(registros)
    print(f"✅ {ano} importado com {len(registros)} registros.\n")

# === IMPORTA AS SAÍDAS DE 2023 A 2025 ===
tratar_saida("data/saidas_2023.xlsx", 2023)
tratar_saida("data/saidas_2024.xlsx", 2024)
tratar_saida("data/saidas_2025.xlsx", 2025)

print("🏁 Finalizado! Todas as saídas foram inseridas com sucesso no banco.")