import pandas as pd

# Filtra as celulas de entrada e saída do arquivo Excel
df_saida = pd.read_excel(
    "data/2025 - Dashboard Piticas Planaltina-DF.xlsx", # caminho do arquivo Excel
    sheet_name = 'Entrada e Saída (R$)', # lê a aba correta
    usecols = 'X:AS', # seleciona as colunas de X até AS
    skiprows= 4, # pula as 4 primeiras linhas
    nrows = 415 # lê até a linha 415
)

# Se em alguma celular não tiver valor, substitui por 0
for col in df_saida.columns:
    df_saida[col] = pd.to_numeric(df_saida[col], errors='coerce').fillna(0) # converte as colunas para numérico, substituindo erros por 0

df_saida.to_csv("data/saida_tratada.csv", index=False) # salva o DataFrame em um arquivo CSV
