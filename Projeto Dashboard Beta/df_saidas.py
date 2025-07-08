import sqlite3
import pandas as pd

# Impede que o Pandas quebre as colunas longas
pd.set_option('display.expand_frame_repr', False)

# Caminho do banco de dados
caminho_banco = 'data/entrada.db'

# Conexão com o banco de dados e leitura da tabela 'saidas'
conexao = sqlite3.connect(caminho_banco)
df_saidas = pd.read_sql('SELECT * FROM saidas', conexao)
conexao.close()

# Convertendo a coluna 'data' para o tipo datetime
df_saidas['data'] = pd.to_datetime(df_saidas['data'], errors='coerce')

# Extraindo ano, mês e dia da coluna 'data'
df_saidas['ano'] = df_saidas['data'].dt.year
df_saidas['mes'] = df_saidas['data'].dt.month
df_saidas['dia'] = df_saidas['data'].dt.day

# Reorganiza colunas
colunas_ordenadas = [
    'data', 'ano', 'mes', 'dia', 'valor', 'categoria', 'descricao'
]
df_saidas = df_saidas[colunas_ordenadas]

# Exibe as primeiras linhas do DataFrame
print(df_saidas.head())