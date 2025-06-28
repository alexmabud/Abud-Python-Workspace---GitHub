import os
import sqlite3
import pandas as pd

# Garante que a pasta 'data' existe
os.makedirs("data", exist_ok=True)

# Caminho do banco
caminho_banco = "data/entrada.db"

# === CRIA A TABELA ===
print("🔧 Criando tabela de entradas no banco...")
conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    valor REAL,
    forma_pagamento TEXT,
    parcelas INTEGER,
    bandeira TEXT,
    categoria TEXT,
    descricao TEXT
)
''')
conexao.commit()
conexao.close()
print("✅ Tabela criada ou já existente.\n")

# === FUNÇÃO DE INSERÇÃO ===
def inserir_entradas(lista):
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()
    for item in lista:
        cursor.execute('''
            INSERT INTO entradas (data, valor, forma_pagamento, parcelas, bandeira, categoria, descricao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            item["data"],
            item["valor"],
            item["forma_pagamento"],
            item["parcelas"],
            item["bandeira"],
            item["categoria"],
            item["descricao"]
        ))
    conexao.commit()
    conexao.close()

# === 2022 ===
print("📥 Importando dados de 2022...")
df_2022 = pd.read_excel("data/entradas_2022.xlsx", header=None)
valor_2022 = float(df_2022.iloc[0, 1])
registro_2022 = [{
    "data": "2022-12-31",
    "valor": valor_2022,
    "forma_pagamento": "Indefinido",
    "parcelas": None,
    "bandeira": None,
    "categoria": "Vendas",
    "descricao": "Total consolidado de entradas em 2022"
}]
inserir_entradas(registro_2022)
print("✅ 2022 importado com sucesso.\n")

# === 2023 ===
print("📥 Importando dados de 2023...")
df_2023 = pd.read_excel("data/entradas_2023.xlsx")
df_2023.columns = [col.strip().lower().replace(" ", "_") for col in df_2023.columns]
formas_2023 = {
    "dinheiro": {"parcelas": 1, "forma": "dinheiro"},
    "pix": {"parcelas": 1, "forma": "pix"},
    "débito": {"parcelas": 1, "forma": "débito"},
    "crédito_1x": {"parcelas": 1, "forma": "crédito"},
    "crédito_2x": {"parcelas": 2, "forma": "crédito"},
    "crédito_3x": {"parcelas": 3, "forma": "crédito"}
}
dados_2023 = []
for _, row in df_2023.iterrows():
    data = pd.to_datetime(row["data"], errors="coerce").strftime("%Y-%m-%d")
    for col, info in formas_2023.items():
        valor = pd.to_numeric(row.get(col), errors="coerce")
        if pd.notnull(valor) and valor > 0:
            dados_2023.append({
                "data": data,
                "valor": float(valor),
                "forma_pagamento": info["forma"],
                "parcelas": info["parcelas"],
                "bandeira": None,
                "categoria": "Vendas",
                "descricao": f"{info['forma'].capitalize()} {info['parcelas']}x"
            })
inserir_entradas(dados_2023)
print(f"✅ 2023 importado com {len(dados_2023)} registros.\n")

# === FUNÇÃO PARA 2024 e 2025 ===
def tratar_entradas_com_bandeiras(caminho_arquivo, ano):
    print(f"📥 Importando dados de {ano}...")
    raw = pd.read_excel(caminho_arquivo, header=None)
    header = raw.iloc[0].tolist()
    df = raw[1:].copy()
    df.columns = header

    colunas = [
        "data", "dinheiro", "pix", "debito",
        "credito_1x_master", "credito_1x_visa", "credito_1x_elo", "credito_1x_amex", "credito_1x_diners",
        "credito_2x_master", "credito_2x_visa", "credito_2x_elo", "credito_2x_amex", "credito_2x_diners",
        "credito_3x_master", "credito_3x_visa", "credito_3x_elo", "credito_3x_amex", "credito_3x_diners"
    ]
    df = df.iloc[:, :len(colunas)]
    df.columns = colunas
    df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")

    registros = []
    for _, row in df.iterrows():
        data = row["data"]
        for col in colunas[1:]:
            valor = pd.to_numeric(row.get(col), errors="coerce")
            if pd.notnull(valor) and valor > 0:
                partes = col.split("_")
                forma = partes[0]
                parcelas = 1
                bandeira = None
                if forma == "credito":
                    parcelas = int(partes[1].replace("x", ""))
                    bandeira = partes[2].capitalize()
                descricao = f"{forma.capitalize()} {parcelas}x {bandeira or ''}".strip()
                registros.append({
                    "data": data,
                    "valor": float(valor),
                    "forma_pagamento": forma,
                    "parcelas": parcelas,
                    "bandeira": bandeira,
                    "categoria": "Vendas",
                    "descricao": descricao
                })
    inserir_entradas(registros)
    print(f"✅ {ano} importado com {len(registros)} registros.\n")

# === IMPORTAR 2024 ===
tratar_entradas_com_bandeiras("data/entradas_2024.xlsx", 2024)

# === IMPORTAR 2025 ===
tratar_entradas_com_bandeiras("data/entradas_2025.xlsx", 2025)

print("🏁 Finalizado! Todas as entradas de 2022 a 2025 foram inseridas com sucesso no banco SQLite.")