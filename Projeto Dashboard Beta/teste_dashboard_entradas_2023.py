import streamlit as st
import pandas as pd
import sqlite3
import os

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("📊 Dashboard Financeiro da Loja")

# Caminho absoluto para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "data", "entrada.db")

# Carregar dados com cache
@st.cache_data
def carregar_dados():
    with sqlite3.connect(db_path) as conn:
        entradas = pd.read_sql_query("SELECT * FROM entradas", conn, parse_dates=['data'])
    return entradas

# Formatar valores em reais
def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Exibir dados por mês para o ano de 2022
def exibir_entradas_por_mes_2022():
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    for mes in range(1, 13):
        st.markdown("---")
        st.subheader(f"📅 Total de Entradas por Dia - {meses[mes]} de 2022")

        dados_mes = entradas[
            (entradas['data'].dt.year == 2022) &
            (entradas['data'].dt.month == mes)
        ]

        if dados_mes.empty:
            st.info(f"Nenhuma entrada encontrada para {meses[mes]} de 2022.")
        else:
            # Agrupar por dia
            agrupado_dia = dados_mes.groupby("data")["valor"].sum().reset_index()
            agrupado_dia["data"] = agrupado_dia["data"].dt.strftime("%d/%m/%Y")
            agrupado_dia["valor"] = agrupado_dia["valor"].apply(formatar_reais)

            # Mostrar tabela
            st.dataframe(agrupado_dia, use_container_width=True, hide_index=True)

            # Total mensal
            total_mes = dados_mes["valor"].sum()
            st.success(f"Total de entradas em {meses[mes]} de 2022: **{formatar_reais(total_mes)}**")

# Carregar os dados
entradas = carregar_dados()

# Exibir entradas de 2022 mês a mês
exibir_entradas_por_mes_2022()