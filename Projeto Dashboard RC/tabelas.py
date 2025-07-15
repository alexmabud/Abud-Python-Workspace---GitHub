import streamlit as st
import pandas as pd
import sqlite3
import os

# Caminho do banco
caminho_data = r'C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Função para carregar qualquer tabela
def carregar_tabela(nome_tabela):
    conn = sqlite3.connect(caminho_banco)
    df = pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)
    conn.close()
    return df

# Título da página
st.title("📋 Visualização de Tabelas")

# --- MENU LATERAL FIXO ---
st.sidebar.header("📂 Navegação")

# Inicializa estado se não existir
if "mostrar_entradas" not in st.session_state:
    st.session_state.mostrar_entradas = False
if "mostrar_saidas" not in st.session_state:
    st.session_state.mostrar_saidas = False

# Botões na sidebar
if st.sidebar.button("📥 Ver Entradas"):
    st.session_state.mostrar_entradas = True
    st.session_state.mostrar_saidas = False

if st.sidebar.button("📤 Ver Saídas"):
    st.session_state.mostrar_entradas = False
    st.session_state.mostrar_saidas = True

# --- CONTEÚDO PRINCIPAL ---
if st.session_state.mostrar_entradas:
    df = carregar_tabela("entrada")
    st.subheader("📥 Tabela de Entradas")

    # Converter datas
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Filtro por ano
    anos_disponiveis = sorted(df["Data"].dt.year.dropna().unique())
    ano_escolhido = st.selectbox("Ano:", anos_disponiveis)

    # Filtrar por ano
    df_ano = df[df["Data"].dt.year == ano_escolhido]

    # Filtro por mês
    nome_meses = {
        0: "Todos",
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    meses_disponiveis = sorted(df_ano["Data"].dt.month.dropna().unique())
    opcoes_radio = [nome_meses[0]] + [nome_meses[m] for m in meses_disponiveis]
    mes_escolhido_nome = st.radio("Mês:", opcoes_radio, horizontal=True)

    # Total do ano
    valor_total_ano = df_ano["Valor"].sum()
    st.markdown(f"### 💰 Total no ano de {ano_escolhido}: R$ {valor_total_ano:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Total do mês e tabela
    if mes_escolhido_nome == "Todos":
        df_exibir = df_ano.copy()
    else:
        mes_num = [k for k, v in nome_meses.items() if v == mes_escolhido_nome][0]
        df_exibir = df_ano[df_ano["Data"].dt.month == mes_num].copy()
        valor_total_mes = df_exibir["Valor"].sum()
        st.markdown(f"#### 📆 Total no mês de {mes_escolhido_nome}: R$ {valor_total_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Formatar tabela final
    df_exibir["Data"] = df_exibir["Data"].dt.strftime("%d/%m/%Y")
    df_exibir["Valor"] = df_exibir["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_exibir = df_exibir[["Data", "Valor"]]  # mostra só colunas desejadas
    st.dataframe(df_exibir, use_container_width=True, hide_index=True)

elif st.session_state.mostrar_saidas:
    st.subheader("📤 Tabela de Saídas")
    st.info("🚧 Em breve: visualização de saídas será implementada.")