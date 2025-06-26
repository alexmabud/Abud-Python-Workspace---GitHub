import pandas as pd
from IPython.display import display

# Exibe todas as colunas e ajusta largura
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Caminho do arquivo
arquivo = "2025 - Dashboard Piticas Planaltina-DF.xlsx"

# Lê a planilha pulando as 3 primeiras linhas que não contêm dados
df = pd.read_excel(arquivo, sheet_name="Entrada e Saída (R$)", skiprows=3)

# Converte datas e remove linhas sem data
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
df = df[df['Data'].notna()]
df.fillna(0, inplace=True)

# Colunas de entrada por forma de pagamento
colunas_entrada_real = [
    'Dinheiro', 'PIX',
    'Master', 'Visa', 'Elo',
    'Master.1', 'Visa.1', 'Elo.1', 'AmEx', 'Diners',
    'Master.2', 'Visa.2', 'Elo.2', 'AmEx.1', 'Diners.1',
    'Master.3', 'Visa.3', 'Elo.3', 'AmEx.2', 'Diners.2'
]

for col in colunas_entrada_real:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Totais por dia
df['Total_do_Dia'] = df[colunas_entrada_real].sum(axis=1)

# Totais por forma de pagamento
df['Total_Dinheiro'] = df['Dinheiro']
df['Total_PIX'] = df['PIX']
df['Total_Debito'] = df[['Master', 'Visa', 'Elo']].sum(axis=1)

df['Total_Credito_1x'] = df[['Master.1', 'Visa.1', 'Elo.1', 'AmEx', 'Diners']].sum(axis=1)
df['Total_Credito_2x'] = df[['Master.2', 'Visa.2', 'Elo.2', 'AmEx.1', 'Diners.1']].sum(axis=1)
df['Total_Credito_3x'] = df[['Master.3', 'Visa.3', 'Elo.3', 'AmEx.2', 'Diners.2']].sum(axis=1)
df['Total_Credito'] = df[['Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x']].sum(axis=1)

# =====================
# 📅 TOTAL POR DIA
total_dia_formatado = df[['Data', 'Total_Dinheiro', 'Total_PIX', 'Total_Debito',
                          'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x',
                          'Total_Credito', 'Total_do_Dia']].copy().head(10)

colunas_valores = [
    'Total_Dinheiro', 'Total_PIX', 'Total_Debito',
    'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x',
    'Total_Credito', 'Total_do_Dia'
]

for col in colunas_valores:
    total_dia_formatado[col] = total_dia_formatado[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

from IPython.display import HTML
display(HTML("<h3 style='font-size:20px; font-weight:bold;'>📅 Entrada Diaria por Forma da Pagamento </h3>"))
display(total_dia_formatado)

# =====================
# 📊 TOTAL POR MÊS
# =====================
df['Mes_Ano'] = df['Data'].dt.to_period('M').astype(str)

total_mensal_pagamentos = df.groupby('Mes_Ano')[[ 
    'Total_Dinheiro', 'Total_PIX', 'Total_Debito',
    'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x',
    'Total_Credito', 'Total_do_Dia'
]].sum().reset_index()

total_mensal_pagamentos.rename(columns={'Total_do_Dia': 'Total_do_Mês'}, inplace=True)

total_mensal_formatado = total_mensal_pagamentos.copy()
for col in colunas_valores:
    nome_col = 'Total_do_Mês' if col == 'Total_do_Dia' else col
    total_mensal_formatado[nome_col] = total_mensal_formatado[nome_col].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

display(HTML("<h3 style='font-size:20px; font-weight:bold;'>📊 Entrada Mensal por Forma de Pagamento </h3>"))
display(total_mensal_formatado)

# =====================
# 📋 TOTAIS DE ENTRADA
# =====================
colunas_totais = [
    'Total_Dinheiro', 'Total_PIX', 'Total_Debito',
    'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x', 'Total_Credito'
]

totais_gerais = df[colunas_totais].sum()
total_geral_entrada = df['Total_do_Dia'].sum()

# Formata valores
totais_gerais_formatado = totais_gerais.apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Calcula porcentagens
porcentagens = (totais_gerais / total_geral_entrada * 100).apply(lambda x: f"{x:.2f}%")

# Cria DataFrame com valores e porcentagens
totais_gerais_df = pd.DataFrame([totais_gerais_formatado, porcentagens])
totais_gerais_df.index = ['Valor Total', '% do Total']
totais_gerais_df['Total Geral de Entradas'] = [
    f"R$ {total_geral_entrada:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    "100%"
]

display(HTML("<h3 style='font-size:20px; font-weight:bold;'>📋 Total de Entrada </h3>"))
display(totais_gerais_df)