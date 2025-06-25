import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Caminho do arquivo Excel
arquivo = "2025 - Dashboard Piticas Planaltina-DF.xlsx"

# Lê a planilha pulando as 3 primeiras linhas
df = pd.read_excel(arquivo, sheet_name="Entrada e Saída (R$)", skiprows=3)

# Converte a coluna 'Data' para o formato datetime
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

# Substitui valores NaN por 0
df.fillna(0, inplace=True)

# Garante que só as colunas numéricas (excluindo 'Data') serão somadas
colunas_numericas = df.select_dtypes(include=['number']).columns
colunas_numericas = colunas_numericas.drop('Total_do_Dia', errors='ignore')  # Evita somar a si mesma
df['Total_do_Dia'] = df[colunas_numericas].sum(axis=1)

# Cria colunas para os totais de Dinheiro e PIX
df['Total_Dinheiro'] = pd.to_numeric(df['Dinheiro'], errors='coerce').fillna(0)
df['Total_PIX'] = pd.to_numeric(df['PIX'], errors='coerce').fillna(0)

# Define colunas de débito e converte para número
colunas_debito = ['Master', 'Visa', 'Elo']
for col in colunas_debito:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
df['Total_Debito'] = df[colunas_debito].sum(axis=1)

# Define colunas de crédito parcelado
credito_1x = ['Master.1', 'Visa.1', 'Elo.1', 'AmEx', 'Diners']
credito_2x = ['Master.2', 'Visa.2', 'Elo.2', 'AmEx.1', 'Diners.1']
credito_3x = ['Master.3', 'Visa.3', 'Elo.3', 'AmEx.2', 'Diners.2']

# Converte todas essas colunas para numérico
for col in credito_1x + credito_2x + credito_3x:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Calcula os totais por tipo de crédito
df['Total_Credito_1x'] = df[credito_1x].sum(axis=1)
df['Total_Credito_2x'] = df[credito_2x].sum(axis=1)
df['Total_Credito_3x'] = df[credito_3x].sum(axis=1)

# Calcula o total geral de crédito
df['Total_Credito'] = df[['Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x']].sum(axis=1)

# Visualiza as 10 primeiras linhas com os totais
print(df[['Data', 'Total_Dinheiro', 'Total_PIX', 'Total_Debito', 'Total_Credito_1x', 'Total_Credito_2x', 'Total_Credito_3x', 'Total_Credito']].head(10))

# Soma total geral por forma de pagamento
totais_gerais = df[['Total_Dinheiro', 'Total_PIX', 'Total_Debito', 'Total_Credito']].sum()
print("\nTotais gerais por forma de pagamento:")
print(totais_gerais)