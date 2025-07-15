import sqlite3
import pandas as pd
import os

# Caminho para os arquivos CSV
caminho_data = r'C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data'

# Carregar os arquivos CSV
df_entradas = pd.read_csv(os.path.join(caminho_data, 'entradas.csv'))
df_saidas = pd.read_csv(os.path.join(caminho_data, 'saidas.csv'))
df_mercadorias = pd.read_csv(os.path.join(caminho_data, 'mercadorias.csv'))

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('dashboard_rc.db')
cursor = conn.cursor()

# Criar tabela de entradas
cursor.execute('''
CREATE TABLE IF NOT EXISTS entrada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Data TEXT,
    Valor REAL,
    Forma_de_Pagamento TEXT,
    Parcelas INTEGER,
    Bandeira TEXT
)
''')

# Criar tabela de saídas
cursor.execute('''
CREATE TABLE IF NOT EXISTS saida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Data TEXT,
    Valor REAL,
    Forma_de_Pagamento TEXT,
    Parcelas INTEGER,
    Categoria TEXT,
    Sub_Categoria TEXT,
    Descricao TEXT
)
''')

# Criar tabela de mercadorias
cursor.execute('''
CREATE TABLE IF NOT EXISTS mercadorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Data TEXT,
    Colecao TEXT,
    Fornecedor TEXT,
    Valor_Mercadoria REAL,
    Frete REAL,
    Forma_Pagamento TEXT,
    Parcelas INTEGER,
    Previsao_Faturamento TEXT,
    Faturamento REAL,
    Previsao_Recebimento TEXT,
    Recebimento REAL,
    Numero_Pedido TEXT,
    Numero_NF TEXT
)
''')

# Inserir os dados nas tabelas
df_entradas.to_sql('entrada', conn, if_exists='append', index=False)
df_saidas.to_sql('saida', conn, if_exists='append', index=False)
df_mercadorias.to_sql('mercadorias', conn, if_exists='append', index=False)

# Finalizar e fechar a conexão
conn.commit()
conn.close()

print(" Banco de dados 'dashboard_rc.db' criado e populado com sucesso!")