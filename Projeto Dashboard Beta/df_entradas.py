import sqlite3
import pandas as pd 

# Impede que o pandas quebre colunas na hora de imprimir
pd.set_option("display.expand_frame_repr", False)

# Caminho do banco de dados
caminho_banco = 'data/entrada.db'

# Conexão com o banco de dados e leitura da tabela 'entradas'
conexao = sqlite3.connect(caminho_banco)
df_entradas = pd.read_sql("SELECT * FROM entradas", conexao)
conexao.close()

# Convertendo a coluna 'data' para o tipo datetime
df_entradas['data'] = pd.to_datetime(df_entradas['data'], errors='coerce')

# Extraindo ano, mês e dia da coluna 'data'
df_entradas['ano'] = df_entradas['data'].dt.year
df_entradas['mes'] = df_entradas['data'].dt.month
df_entradas['dia'] = df_entradas['data'].dt.day

# Reorganiza as colunas (sem a coluna 'descricao')
colunas_ordenadas = [
    "data", "ano", "mes", "dia",
    "valor", "forma_pagamento", "parcelas", "bandeira", "categoria"
]
df_entradas = df_entradas[colunas_ordenadas]

# Exibe as primeiras linhas do DataFrame final
print(df_entradas.head())

