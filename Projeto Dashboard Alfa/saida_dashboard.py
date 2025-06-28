import pandas as pd
from IPython.display import display, HTML

# Lê as colunas X (Data) e AS (Total) da planilha
df_raw = pd.read_excel(
    "data/2025 - Dashboard Piticas Planaltina-DF.xlsx",
    sheet_name='Entrada e Saída (R$)',
    usecols='X,AS',
    skiprows=3  # começa na linha onde estão as datas
)

#  Renomeia as colunas
df_raw.columns = ['Data', 'Saida']

# Corrige datas com ano errado (2024 → 2025) 
df_raw['Data'] = pd.to_datetime(df_raw['Data'], dayfirst=True, errors='coerce')
df_raw['Data'] = df_raw['Data'].apply(lambda x: x.replace(year=2025) if pd.notnull(x) and x.year == 2024 else x)

# Converte valores de saída para número e preenche vazios com 0 
df_raw['Saida'] = pd.to_numeric(df_raw['Saida'], errors='coerce').fillna(0)

# Remove as linhas que representam totais do mês (Data nula) 
df_saida = df_raw[df_raw['Data'].notna()].copy()

# Salva CSV corrigido
df_saida.to_csv("data/saida_tratada_corrigido.csv", index=False)

# Total por dia 
df_diaria = df_saida.copy()

#  Total por mês
df_saida['Mes_Ano'] = df_saida['Data'].dt.to_period('M')
saida_mensal = df_saida.groupby('Mes_Ano')['Saida'].sum().reset_index()
saida_mensal['Mes_Ano'] = saida_mensal['Mes_Ano'].astype(str)
saida_mensal.rename(columns={'Saida': 'Total_do_Mes'}, inplace=True)

# Total por ano
df_saida['Ano'] = df_saida['Data'].dt.year
saida_anual = df_saida.groupby('Ano')['Saida'].sum().reset_index()
saida_anual.rename(columns={'Saida': 'Total_do_Ano'}, inplace=True)

# Formata os valores como R$
df_diaria_fmt = df_diaria.copy()
saida_mensal_fmt = saida_mensal.copy()
saida_anual_fmt = saida_anual.copy()

df_diaria_fmt['Saida'] = df_diaria_fmt['Saida'].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
saida_mensal_fmt['Total_do_Mes'] = saida_mensal_fmt['Total_do_Mes'].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
saida_anual_fmt['Total_do_Ano'] = saida_anual_fmt['Total_do_Ano'].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))

# Exibe os resultados formatados 
display(HTML("<h3>📅 Total de Saída por Dia</h3>"))
display(df_diaria_fmt.head(15))

display(HTML("<h3>📅 Total de Saída por Mês</h3>"))
display(saida_mensal_fmt)

display(HTML("<h3>📅 Total de Saída por Ano</h3>"))
display(saida_anual_fmt)