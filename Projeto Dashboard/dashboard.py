import pandas as pd
pd.set_option('display.max_columns', None) # Configura o pandas para exibir todas as colunas

arquivo = "2025 - Dashboard Piticas Planaltina-DF.xlsx" # Nome do arquivo Excel
df = pd.read_excel(arquivo, sheet_name="Entrada e Saída (R$)", skiprows=3) # Lê a planilha do arquivo Excel

df['Data'] = pd.to_datetime(df['Data'], errors='coerce') # Converte a coluna 'Data' para o formato datetime

print(df.head()) # Exibe as primeiras linhas do DataFrame

