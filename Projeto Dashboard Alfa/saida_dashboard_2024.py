import pandas as pd

# Caminho local do arquivo CSV
caminho_csv = r"C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard\data\saida_tratada_2024.csv"

# Lê o CSV sem cabeçalho e define os nomes das colunas
df = pd.read_csv(caminho_csv, names=['Data', 'Saida'], header=None, sep=',')

# Converte a coluna Data para datetime
df['Data'] = pd.to_datetime(df['Data'], format="%Y-%m-%d", errors='coerce')

# Adiciona coluna do mês
df['Mes'] = df['Data'].dt.to_period('M')

# DataFrame 1: Saída por dia com mês
df_diario = df.copy()

# DataFrame 2: Soma por mês
df_mensal = df.groupby('Mes')['Saida'].sum().reset_index()
df_mensal['Mes'] = df_mensal['Mes'].dt.to_timestamp()

# DataFrame 3: Soma do ano
df_anual = pd.DataFrame({
    'Ano': [df['Data'].dt.year.iloc[0]],
    'Saida_Total': [df['Saida'].sum()]
})

# Exibe os resultados
print("==== Saída por Dia ====")
print(df_diario.head())

print("\n==== Saída Mensal ====")
print(df_mensal)

print("\n==== Saída Anual ====")
print(df_anual)