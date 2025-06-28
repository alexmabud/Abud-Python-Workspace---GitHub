import pandas as pd
from IPython.display import display, HTML

# Lê o arquivo CSV 
arquivo = "data/entrada_tratada_2024_corrigida_final.csv"
df = pd.read_csv(arquivo)

# Converte a coluna de data 
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
df = df[df['Data'].notna()]
df.fillna(0, inplace=True)

# Converte colunas financeiras para números 
colunas_entrada_real = [
    'Dinheiro', 'PIX',
    'Master', 'Visa', 'Elo',
    'Master.1', 'Visa.1', 'Elo.1', 'AmEx', 'Diners',
    'Master.2', 'Visa.2', 'Elo.2', 'AmEx.1', 'Diners.1',
    'Master.3', 'Visa.3', 'Elo.3', 'AmEx.2', 'Diners.2'
]

for col in colunas_entrada_real:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 4. Totais por dia e categorias
df['Total_do_Dia'] = df[colunas_entrada_real].sum(axis=1)
df['Total_Dinheiro'] = df['Dinheiro']
df['Total_PIX'] = df['PIX']
df['Total_Debito'] = df[['Master', 'Visa', 'Elo']].sum(axis=1)
df['Total_Credito_1x'] = df[['Master.1', 'Visa.1', 'Elo.1', 'AmEx', 'Diners']].sum(axis=1)
df['Total_Credito_2x'] = df[['Master.2', 'Visa.2', 'Elo.2', 'AmEx.1', 'Diners.1']].sum(axis=1)
df['Total_Credito_3x'] = df[['Master.3', 'Visa.3', 'Elo.3', 'AmEx.2', 'Diners.2']].sum(axis=1)
df['Total_Credito'] = df[['Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x']].sum(axis=1)

# Tabela formatada por dia 
df_diaria_fmt = df[['Data', 'Total_Dinheiro', 'Total_PIX', 'Total_Debito',
                    'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x',
                    'Total_Credito', 'Total_do_Dia']].copy()

for col in df_diaria_fmt.columns[1:]:
    df_diaria_fmt[col] = df_diaria_fmt[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

display(HTML("<h3>📅 Entrada Diária por Forma de Pagamento (2024)</h3>"))
display(df_diaria_fmt.head(15))

# Totais por mês
df['Mes_Ano'] = df['Data'].dt.to_period('M').astype(str)
mensal = df.groupby('Mes_Ano')[[
    'Total_Dinheiro', 'Total_PIX', 'Total_Debito',
    'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x',
    'Total_Credito', 'Total_do_Dia'
]].sum().reset_index()

mensal.rename(columns={'Total_do_Dia': 'Total_do_Mês'}, inplace=True)

# Formata valores
mensal_fmt = mensal.copy()
for col in mensal_fmt.columns[1:]:
    mensal_fmt[col] = mensal_fmt[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

display(HTML("<h3>📊 Entrada Mensal por Forma de Pagamento (2024)</h3>"))
display(mensal_fmt)

# Totais gerais
totais_colunas = ['Total_Dinheiro', 'Total_PIX', 'Total_Debito',
                  'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x', 'Total_Credito']

totais_gerais = df[totais_colunas].sum()
total_geral = df['Total_do_Dia'].sum()

totais_formatados = totais_gerais.apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
porcentagens = (totais_gerais / total_geral * 100).apply(lambda x: f"{x:.2f}%")

tabela_totais = pd.DataFrame([totais_formatados, porcentagens])
tabela_totais.index = ['Valor Total', '% do Total']
tabela_totais['Total Geral de Entradas'] = [
    f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    "100%"
]

display(HTML("<h3>📋 Total de Entrada no Ano de 2024</h3>"))
display(tabela_totais)