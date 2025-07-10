import streamlit as st
import pandas as pd
import sqlite3
import os

# Configuração da página -  comando para definir o título da aba e titulo da página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("📊 Dashboard Financeiro da Loja")

# Caminho absoluto para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "data", "entrada.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Carregar os dados do banco
@st.cache_data
def carregar_dados():
    entradas = pd.read_sql_query("SELECT * FROM entradas", conn, parse_dates=['data'])
    
    return entradas

entradas = carregar_dados()

# Mostrar os dados de 2022
st.subheader("📆 Visualização dos Dados de 2022")
entradas_2022 = entradas[entradas['data'].dt.year == 2022]

if entradas_2022.empty:
    st.info("Nenhuma entrada encontrada para 2022.")
else:
    entradas_2022_formatado = entradas_2022.copy()
    entradas_2022_formatado["data"] = entradas_2022_formatado["data"].dt.strftime("%d/%m/%Y")
    entradas_2022_formatado["valor"] = entradas_2022_formatado["valor"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
    )

    # Mostrar só data e valor
    st.dataframe(
        entradas_2022_formatado[["data", "valor"]],
        use_container_width=True,
        hide_index=True
    )