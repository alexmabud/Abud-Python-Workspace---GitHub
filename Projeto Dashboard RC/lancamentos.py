import streamlit as st
import sqlite3
import os
import hashlib
import pandas as pd
import re
from datetime import date
from workalendar.america import BrazilDistritoFederal
from datetime import timedelta

# === CSS personalizado ============================================================================================
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #111827;
        padding-top: 2rem;
    }
    .sidebar-button {
        background-color: #1f2937;
        color: white;
        border: none;
        padding: 0.8rem;
        border-radius: 8px;
        width: 100%;
        margin-bottom: 1rem;
        font-weight: bold;
        text-align: left;
    }
    .sidebar-button:hover {
        background-color: #374151;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# === Caminho do banco de dados ======================================================================================
caminho_data = r'C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# === Função para carregar tabela ====================================================================================
def carregar_tabela(nome_tabela):
    try:
        with sqlite3.connect(caminho_banco) as conn:
            return pd.read_sql(f"SELECT * FROM {nome_tabela}", conn)
    except Exception as e:
        st.error(f"Erro ao carregar tabela '{nome_tabela}': {e}")
        return pd.DataFrame()

# === Criação da tabela de usuários se não existir ==================================================================
with sqlite3.connect(caminho_banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL,
            ativo INTEGER NOT NULL
        )
    """)

# === Função para gerar hash da senha ================================================================================
def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# === Função para validar força da senha =============================================================================
def senha_forte(senha):
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha):  # letra maiúscula
        return False
    if not re.search(r"[a-z]", senha):  # letra minúscula
        return False
    if not re.search(r"[0-9]", senha):  # número
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):  # símbolo
        return False
    return True

# === Função de verificação de acesso por perfil =====================================================================
def verificar_acesso(perfis_permitidos):
    usuario = st.session_state.get("usuario_logado")
    if not usuario or usuario.get("perfil") not in perfis_permitidos:
        st.warning("🚫 Acesso não autorizado.")
        st.stop()

# === Exibir usuário logado =========================================================================================
def exibir_usuario_logado():
    usuario = st.session_state.get("usuario_logado")
    if usuario:
        st.markdown(f"👤 **{usuario['nome']}** — Perfil: `{usuario['perfil']}`")
        st.markdown("---")

# === LOGIN DO USUÁRIO ===============================================================================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if not st.session_state.usuario_logado:
    st.markdown("## 🔐 Login")
    with st.form("login_form"):
        email_login = st.text_input("Email")
        senha_login = st.text_input("Senha", type="password")
        login_submitted = st.form_submit_button("Entrar")

        if login_submitted:
            with sqlite3.connect(caminho_banco) as conn:
                senha_login_hash = gerar_hash_senha(senha_login)
                cursor = conn.execute(
                    "SELECT nome, email, perfil FROM usuarios WHERE email = ? AND senha = ? AND ativo = 1",
                    (email_login, senha_login_hash)
                )
                usuario = cursor.fetchone()

            if usuario:
                st.session_state.usuario_logado = {
                    "nome": usuario[0],
                    "email": usuario[1],
                    "perfil": usuario[2]
                }
                st.success(f"✅ Bem-vindo, {usuario[0]}!")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha inválidos, ou usuário inativo.")

    st.stop()

# === Função para limpar todas as páginas =============================================================================
def limpar_todas_as_paginas():
    chaves = [
        "mostrar_metas", "mostrar_entradas", "mostrar_saidas", "mostrar_lancamentos_do_dia",
        "mostrar_mercadorias", "mostrar_cartao_credito", "mostrar_emprestimos_financiamentos",
        "mostrar_contas_pagar", "mostrar_taxas_maquinas", "mostrar_usuarios",
        "mostrar_fechamento_caixa", "mostrar_correcao_caixa"  # 👈 Adiciona aqui
    ]
    for chave in chaves:
        st.session_state[chave] = False

# === Função para obter o último dia útil antes de uma data base ====================================================
cal = BrazilDistritoFederal()

def ultimo_dia_util(data_base):
    """
    Retorna o último dia útil antes da data_base,
    considerando fins de semana e feriados (DF).
    """
    data = data_base - timedelta(days=1)
    while not cal.is_working_day(data):
        data -= timedelta(days=1)
    return data

# === Inicializa estados padrão =======================================================================================
estados_iniciais = {
    "mostrar_entradas": False,
    "mostrar_saidas": False,
    "mostrar_lancamentos_do_dia": False,
    "mostrar_mercadorias": False,
    "mostrar_cartao_credito": False,
    "mostrar_emprestimos_financiamentos": False,
    "mostrar_contas_pagar": False,
    "mostrar_taxas_maquinas": False,
    "mostrar_usuarios": False,
    "mostrar_fechamento_caixa": False,
    "mostrar_correcao_caixa": False,
    "mes_selecionado": 1,
    "mes_saida_selecionado": 1,
    "mes_mercadoria": 1
}
for chave, valor in estados_iniciais.items():
    st.session_state.setdefault(chave, valor)

# === Nome dos meses ================================================================================================
nome_meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}


# === SIDEBAR ========================================================================================================
usuario = st.session_state.get("usuario_logado")
perfil_usuario = usuario.get("perfil") if usuario else None

# Mostrar nome e perfil
if usuario:
    st.sidebar.markdown(f"👤 **{usuario['nome']}**\n🔐 Perfil: `{usuario['perfil']}`")

    # Botão Sair (visível para todos os perfis)
    if st.sidebar.button("🚪 Sair", key="botao_sair"):
        st.session_state.usuario_logado = None
        st.rerun()

    # Espaçamento e separador
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

# === TÍTULO PRINCIPAL ===============================================================================================
st.title("")  # pode ser atualizado depois dinamicamente

# === Controle da página principal ===================================================================================
if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = None

usuario = st.session_state.get("usuario_logado")
perfil_usuario = usuario.get("perfil") if usuario else None

# Define as opções do menu conforme o perfil
opcoes_disponiveis = []

if perfil_usuario in ["Administrador", "Gerente", "Vendedor"]:
    opcoes_disponiveis.append("🎯 Metas")

if perfil_usuario in ["Administrador", "Gerente"]:
    opcoes_disponiveis.append("💼 Fechamento de Caixa")

if perfil_usuario in ["Administrador", "Gerente"]:
    opcoes_disponiveis.append("📊 Dashboard")

if perfil_usuario in ["Administrador", "Gerente", "Vendedor"]:
    opcoes_disponiveis.append("🧾 Lançamentos")

if perfil_usuario in ["Administrador", "Gerente"]:
    opcoes_disponiveis.append("📉 DRE")

if perfil_usuario == "Administrador":
    opcoes_disponiveis.append("🛠️ Cadastro")

# Menu lateral com base nas permissões
st.sidebar.markdown("#### 🧭 Selecione uma opção abaixo:")
st.sidebar.markdown('<div class="sidebar-opcoes"> Opções:</div>', unsafe_allow_html=True)
opcao = st.sidebar.radio("", opcoes_disponiveis)

# Atualiza a página ativa
if st.session_state["pagina_atual"] != opcao:
    limpar_todas_as_paginas()
    st.session_state["pagina_atual"] = opcao

# Atualiza o título principal
st.title(opcao)

# === Submenu: Metas ================================================================================================
if opcao == "🎯 Metas":
    st.markdown("🎯 Metas em desenvolvimento...")

# === Submenu: Dashboard ============================================================================================
elif opcao == "📊 Dashboard":
    st.markdown("📊 Dashboard em desenvolvimento...")

# === Submenu: DRE ================================================================================================
elif opcao == "📉 DRE":
    st.markdown("📉 DRE em desenvolvimento...")

# === Submenu: Lançamentos ========================================================================================
elif opcao == "🧾 Lançamentos":
    st.markdown("📌 Selecione uma opção no menu à esquerda para visualização.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔽 Lançamentos")

    if st.sidebar.button("📅 Lançamentos do Dia"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_lancamentos_do_dia = True

    if perfil_usuario in ["Administrador", "Gerente"]:
        if st.sidebar.button("📥 Ver Entradas"):
            limpar_todas_as_paginas()
            st.session_state.mostrar_entradas = True

        if st.sidebar.button("📤 Ver Saídas"):
            limpar_todas_as_paginas()
            st.session_state.mostrar_saidas = True

        if st.sidebar.button("📦 Ver Mercadorias"):
            limpar_todas_as_paginas()
            st.session_state.mostrar_mercadorias = True

        if st.sidebar.button("💳 Ver Cartão de Crédito"):
            limpar_todas_as_paginas()
            st.session_state.mostrar_cartao_credito = True

        if st.sidebar.button("📋 Ver Contas a Pagar"):
            limpar_todas_as_paginas()
            st.session_state.mostrar_contas_pagar = True

        if st.sidebar.button("💰 Empréstimos e Financiamentos"):
            limpar_todas_as_paginas()
            st.session_state.mostrar_emprestimos_financiamentos = True

# === Submenu: Fechamento de Caixa ================================================================================
elif opcao == "💼 Fechamento de Caixa":
  
    data_fechamento = st.date_input("Data do Fechamento", value=date.today())
    data_fechamento_str = str(data_fechamento)
    data_util_anterior = ultimo_dia_util(data_fechamento)

    col1, col2, col3 = st.columns(3)
    with col1:
        banco_1 = st.number_input("Saldo Banco 1", min_value=0.0, step=10.0)
    with col2:
        banco_2 = st.number_input("Saldo Banco 2", min_value=0.0, step=10.0)
    with col3:
        banco_4 = st.number_input("Saldo Banco 4", min_value=0.0, step=10.0)

    col4, col5 = st.columns(2)
    with col4:
        caixa_loja = st.number_input("Caixa", min_value=0.0, step=10.0)
    with col5:
        caixa_casa = st.number_input("Caixa 2", min_value=0.0, step=10.0)

# === Entradas confirmadas (Pix/Dinheiro do dia + Crédito/Débito do D-1 útil) ===
    df_entrada = carregar_tabela("entrada")
    df_entrada["Data"] = pd.to_datetime(df_entrada["Data"], errors="coerce")

    df_confirmadas = df_entrada[
        (
            ((df_entrada["Forma_de_Pagamento"].astype(str).str.upper().isin(["PIX", "DINHEIRO"])) &
            (df_entrada["Data"].dt.date == data_fechamento)) |
            ((df_entrada["Forma_de_Pagamento"].astype(str).str.upper().isin(["CRÉDITO", "CREDITO", "DÉBITO", "DEBITO"])) &
            (df_entrada["Data"].dt.date == data_util_anterior))
        )
    ]
    total_entradas = df_confirmadas["Valor"].sum()

    # === Saídas do dia ===
    df_saida = carregar_tabela("saida")
    df_saida["Data"] = pd.to_datetime(df_saida["Data"], errors="coerce")
    df_saida_dia = df_saida[df_saida["Data"].dt.date == data_fechamento]
    total_saidas = df_saida_dia["Valor"].sum()

    # === Correções manuais do dia ===
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.execute("SELECT SUM(valor) FROM correcao_caixa WHERE data = ?", (data_fechamento_str,))
        total_correcao = cursor.fetchone()[0] or 0.0

    # === Cálculo do saldo esperado ===
    saldo_esperado = total_entradas - total_saidas + total_correcao

    # === Valor informado real (somado pelos campos digitados)
    valor_informado = banco_1 + banco_2 + banco_4 + caixa_loja + caixa_casa
    diferenca = valor_informado - saldo_esperado

    # === Exibição do Resumo
    st.markdown("### 📊 Resumo do Fechamento do Dia")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"Entradas confirmadas: R$ {total_entradas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col2:
        st.error(f"Saídas: R$ {total_saidas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col3:
        st.success(f"Correções: R$ {total_correcao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown(f"### 💰 Saldo Esperado: R$ {saldo_esperado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(f"### 💵 Valor Informado: R$ {valor_informado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if diferenca == 0:
        st.success("✅ Caixa Correto! Não há diferença.")
    else:
        cor = "🟢" if diferenca > 0 else "🔴"
        st.warning(f"### {cor} Diferença: R$ {diferenca:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if st.button("💾 Salvar Fechamento"):
        try:
            with sqlite3.connect(caminho_banco) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS fechamento_caixa (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data TEXT NOT NULL,
                        banco_1 REAL,
                        banco_2 REAL,
                        banco_4 REAL,
                        caixa_loja REAL,
                        caixa_casa REAL,
                        entradas_confirmadas REAL,
                        saidas REAL,
                        correcao REAL,
                        saldo_esperado REAL,
                        valor_informado REAL,
                        diferenca REAL
                    )
                """)

                conn.execute("""
                    INSERT INTO fechamento_caixa (
                        data, banco_1, banco_2, banco_4, caixa_loja, caixa_casa,
                        entradas_confirmadas, saidas, correcao, saldo_esperado, valor_informado, diferenca
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(data_fechamento), banco_1, banco_2, banco_4, caixa_loja, caixa_casa,
                    total_entradas, total_saidas, total_correcao,
                    saldo_esperado, valor_informado, diferenca
                ))
                conn.commit()
            st.success("✅ Fechamento salvo com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

# === Submenu: Cadastro ============================================================================================
elif opcao == "🛠️ Cadastro":
    st.markdown("📌 Selecione uma opção no menu à esquerda para visualização.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔽 Cadastro")

    if st.sidebar.button("⚙️ Taxas de Máquinas"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_taxas_maquinas = True

    if st.sidebar.button("👥 Usuários"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_usuarios = True

    if st.sidebar.button("🛠️ Correção de Caixa"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_correcao_caixa = True

# === Página: Lançamentos do Dia =====================================================================================
if st.session_state.get("mostrar_lancamentos_do_dia", False):
    st.markdown("### 📅 Lançamentos do Dia")
    st.info("Funcionalidade em desenvolvimento...")

# === Página: Entradas ==============================================================================================
if st.session_state.get("mostrar_entradas", False):
    st.subheader("📥 Tabela de Entradas")

    df = carregar_tabela("entrada")
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Total geral
    total_geral = df["Valor"].sum()
    st.success(f"### 📊 Total de todos os anos de Entradas: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Totais por ano
    st.markdown("### 📆 Totais por ano:")
    df["Ano"] = df["Data"].dt.year.astype("Int64")
    totais_por_ano = df.groupby("Ano")["Valor"].sum().reset_index()
    totais_por_ano.columns = ["Ano", "Total"]
    totais_por_ano["Ano"] = totais_por_ano["Ano"].astype(int).astype(str)
    totais_por_ano["Total"] = totais_por_ano["Total"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(totais_por_ano, use_container_width=True, hide_index=True)

    # Filtro por ano
    anos = sorted(df["Data"].dt.year.dropna().unique())
    st.markdown("### 📅 Selecione o ano:")
    ano = st.selectbox("", anos)
    df_ano = df[df["Data"].dt.year == ano]
    total_ano = df_ano["Valor"].sum()
    st.success(f"### 💰 Total de Entradas no ano de {ano}: R$ {total_ano:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Totais por mês
    totais_por_mes = df_ano.groupby(df_ano["Data"].dt.month)["Valor"].sum().reindex(range(1, 13), fill_value=0).reset_index()
    totais_por_mes.columns = ["Mês", "Total"]
    totais_por_mes["Mês"] = totais_por_mes["Mês"].map(nome_meses)
    totais_por_mes["Total"] = totais_por_mes["Total"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown("### 📈 Totais por mês no ano selecionado")
    st.dataframe(totais_por_mes, use_container_width=True, hide_index=True)

    # Filtro por mês
    st.markdown("### 📅 Selecione o mês:")
    for inicio in [1, 7]:
        colunas = st.columns(6)
        for i in range(inicio, inicio + 6):
            with colunas[i - inicio]:
                if st.button(nome_meses[i], key=f"mes_{i}"):
                    st.session_state.mes_selecionado = i

    mes = st.session_state.mes_selecionado
    nome_mes = nome_meses[mes]
    df_mes = df_ano[df_ano["Data"].dt.month == mes].copy()
    total_mes = df_mes["Valor"].sum()
    st.success(f"### 🗓️ Total de Entradas no mês de {nome_mes}: R$ {total_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Tabela resumida (Data + Valor)
    df_mes_resumo = df_mes[["Data", "Valor"]].copy()
    df_mes_resumo["Data"] = pd.to_datetime(df_mes_resumo["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
    df_mes_resumo["Valor"] = df_mes_resumo["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(df_mes_resumo, use_container_width=True, hide_index=True)

    # Tabela detalhada
    st.markdown("### 🔍 Tabela detalhada de lançamentos do mês")
    df_detalhado = df_mes.copy()
    df_detalhado["Data"] = pd.to_datetime(df_detalhado["Data"], errors="coerce")
    df_detalhado = df_detalhado.sort_values(by="Data")
    df_detalhado["Data"] = df_detalhado["Data"].dt.strftime("%d/%m/%Y")
    if "Valor" in df_detalhado.columns:
        df_detalhado["Valor"] = df_detalhado["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    for col in ["id", "Ano"]:
        if col in df_detalhado.columns:
            df_detalhado = df_detalhado.drop(columns=[col])
    st.dataframe(df_detalhado, use_container_width=True, hide_index=True)

# === Página: Saídas ================================================================================================
if st.session_state.get("mostrar_saidas", False):
    st.subheader("📤 Tabela de Saídas")

    df = carregar_tabela("saida")
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Total geral
    valor_total_geral = df["Valor"].sum()
    st.error(f"### 📊 Total de todos os anos de Saídas: R$ {valor_total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Totais por ano
    st.markdown("### 📆 Totais por ano:")
    df["Ano"] = df["Data"].dt.year.astype("Int64")
    totais_por_ano = df.groupby("Ano")["Valor"].sum().reset_index()
    totais_por_ano.columns = ["Ano", "Total"]
    totais_por_ano["Ano"] = totais_por_ano["Ano"].astype(int).astype(str)
    totais_por_ano["Total"] = totais_por_ano["Total"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(totais_por_ano, use_container_width=True, hide_index=True)

    # Filtro por ano
    anos_disponiveis = sorted(df["Data"].dt.year.dropna().unique())
    st.markdown("### 📅 Selecione o ano:")
    ano_escolhido = st.selectbox("", anos_disponiveis, key="ano_saida")
    df_ano = df[df["Data"].dt.year == ano_escolhido]

    # Total por ano
    valor_total_ano = df_ano["Valor"].sum()
    st.error(f"### 💰 Total no ano de {ano_escolhido}: R$ {valor_total_ano:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Totais por mês
    totais_por_mes = df_ano.groupby(df_ano["Data"].dt.month)["Valor"].sum().reindex(range(1, 13), fill_value=0).reset_index()
    totais_por_mes.columns = ["Mês", "Total"]
    totais_por_mes["Mês"] = totais_por_mes["Mês"].map(nome_meses)
    totais_por_mes["Total"] = totais_por_mes["Total"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown("### 📈 Totais por mês no ano selecionado")
    st.dataframe(totais_por_mes, use_container_width=True, hide_index=True)

    # Filtro por mês
    st.markdown("### 📅 Selecione o mês:")
    for inicio in [1, 7]:
        colunas = st.columns(6)
        for i in range(inicio, inicio + 6):
            with colunas[i - inicio]:
                if st.button(nome_meses[i], key=f"saida_mes_{i}"):
                    st.session_state.mes_saida_selecionado = i

    mes_saida = st.session_state.mes_saida_selecionado
    nome_mes = nome_meses[mes_saida]
    df_mes = df_ano[df_ano["Data"].dt.month == mes_saida].copy()
    valor_total_mes = df_mes["Valor"].sum()
    st.error(f"### 🗓️ Total de Saídas no mês de {nome_mes}: R$ {valor_total_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Tabela resumida
    df_mes_resumo = df_mes[["Data", "Valor"]].copy()
    df_mes_resumo["Data"] = pd.to_datetime(df_mes_resumo["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
    df_mes_resumo["Valor"] = df_mes_resumo["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.dataframe(df_mes_resumo, use_container_width=True, hide_index=True)

    # Tabela detalhada
    st.markdown("### 🔍 Tabela detalhada de lançamentos do mês")
    df_detalhado = df_mes.copy()
    df_detalhado["Data"] = pd.to_datetime(df_detalhado["Data"], errors="coerce")
    df_detalhado = df_detalhado.sort_values(by="Data")
    df_detalhado["Data"] = df_detalhado["Data"].dt.strftime("%d/%m/%Y")
    if "Valor" in df_detalhado.columns:
        df_detalhado["Valor"] = df_detalhado["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    for col in ["id", "Ano"]:
        if col in df_detalhado.columns:
            df_detalhado = df_detalhado.drop(columns=[col])
    st.dataframe(df_detalhado, use_container_width=True, hide_index=True)

# === Página: Mercadorias ===========================================================================================
if st.session_state.get("mostrar_mercadorias", False):
    st.subheader("📦 Tabela de Mercadorias")

    df = carregar_tabela("mercadorias")

    if df.empty:
        st.warning("⚠️ Não foi possível carregar a tabela de mercadorias.")
    else:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

        # Filtro por ano
        anos = sorted(df["Data"].dt.year.dropna().unique())
        st.markdown("### 📅 Selecione o ano:")
        ano = st.selectbox("", anos, key="ano_mercadoria")
        df_ano = df[df["Data"].dt.year == ano]

        # Total do ano
        if "Valor_Mercadoria" in df_ano.columns:
            df_ano["Valor_Mercadoria"] = pd.to_numeric(df_ano["Valor_Mercadoria"], errors="coerce")
            total_ano = df_ano["Valor_Mercadoria"].sum()
            st.info(f"### 📊 Total de Mercadorias no ano de {ano}: R$ {total_ano:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Filtro por mês
        st.markdown("### 📅 Selecione o mês:")
        for inicio in [1, 7]:
            colunas = st.columns(6)
            for i in range(inicio, inicio + 6):
                with colunas[i - inicio]:
                    if st.button(nome_meses[i], key=f"mes_mercadoria_{i}"):
                        st.session_state.mes_mercadoria = i

        mes = st.session_state.get("mes_mercadoria", 1)
        nome_mes = nome_meses[mes]
        df_mes = df_ano[df_ano["Data"].dt.month == mes].copy()

        st.markdown(f"### 📋 Mercadorias de {nome_mes} de {ano}")

        if df_mes.empty:
            st.warning("Nenhum registro encontrado para o mês selecionado.")
        else:
            # Total do mês
            if "Valor_Mercadoria" in df_mes.columns:
                df_mes["Valor_Mercadoria"] = pd.to_numeric(df_mes["Valor_Mercadoria"], errors="coerce")
                total_mes = df_mes["Valor_Mercadoria"].sum()
                st.info(f"### 📦 Total de Mercadorias no mês: R$ {total_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            # Formatando datas
            df_mes["Data"] = pd.to_datetime(df_mes["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
            for col in ["Previsao_Faturamento", "Faturamento", "Previsao_Recebimento", "Recebimento"]:
                if col in df_mes.columns:
                    df_mes[col] = pd.to_datetime(df_mes[col], errors="coerce").dt.strftime("%d/%m/%y")

            # Formatando valores
            df_mes["Valor_Mercadoria"] = df_mes["Valor_Mercadoria"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else ""
            )

            # Limpando colunas numéricas
            for col in ["Numero_Pedido", "Numero_NF"]:
                if col in df_mes.columns:
                    df_mes[col] = df_mes[col].astype(str).str.replace(r"[^\d]", "", regex=True)

            # Exibir colunas organizadas
            colunas_exibir = [
                "Data", "Colecao", "Fornecedor", "Valor_Mercadoria", "Frete", "Forma_Pagamento",
                "Parcelas", "Previsao_Faturamento", "Faturamento",
                "Previsao_Recebimento", "Recebimento", "Numero_Pedido", "Numero_NF"
            ]
            colunas_presentes = [col for col in colunas_exibir if col in df_mes.columns]
            df_mes = df_mes.loc[:, colunas_presentes]

            st.dataframe(df_mes, use_container_width=True, hide_index=True)

# === Página: Contas a Pagar ========================================================================================
if st.session_state.get("mostrar_contas_pagar", False):
    st.subheader("📄 Contas a Pagar")
    st.info("🔧 Em desenvolvimento...")

# === Página: Cartão de Crédito ======================================================================================
if st.session_state.get("mostrar_cartao_credito", False):
    st.subheader("💳 Cartão de Crédito")
    st.info("🔧 Em desenvolvimento...")

# === Página: Empréstimos e Financiamentos ==========================================================================
if st.session_state.get("mostrar_emprestimos_financiamentos", False):
    st.subheader("🏦 Empréstimos e Financiamentos")
    st.info("🔧 Em desenvolvimento...")

# === Página: Cadastro de Taxas das Máquinas de Cartão ============================================================
if st.session_state.get("mostrar_taxas_maquinas", False):
    st.subheader("💳 Cadastro de Taxas das Máquinas de Cartão")

    forma_pagamento = st.selectbox("Forma de Pagamento", ["Débito", "Crédito"], index=1)

    # Bandeiras conforme a forma de pagamento
    if forma_pagamento == "Débito":
        opcoes_bandeiras = ["Visa", "Master", "Elo"]
    else:
        opcoes_bandeiras = ["Visa", "Master", "Elo", "Amex", "DinersClub"]

    st.divider()

    # Formulário
    with st.form("form_taxas_maquinas"):
        col1, col2, col3 = st.columns(3)

        with col1:
            bandeira = st.selectbox("Bandeira", opcoes_bandeiras)

        with col2:
            if forma_pagamento == "Débito":
                parcelas = 1
                st.markdown("Parcelas")
                st.number_input("🔒 Não se aplica para Débito", value=1, disabled=True, label_visibility="collapsed")
            else:
                parcelas = st.selectbox("Parcelas", list(range(1, 13)), index=0)

        with col3:
            taxa = st.number_input("Taxa (%)", min_value=0.0, format="%.2f", step=0.01)

        submitted = st.form_submit_button("Salvar")

        if submitted:
            with sqlite3.connect(caminho_banco) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS taxas_maquinas (
                        forma_pagamento TEXT NOT NULL,
                        bandeira TEXT NOT NULL,
                        parcelas INTEGER NOT NULL,
                        taxa_percentual REAL NOT NULL,
                        PRIMARY KEY (forma_pagamento, bandeira, parcelas)
                    )
                """)
                conn.execute("""
                    INSERT OR REPLACE INTO taxas_maquinas (forma_pagamento, bandeira, parcelas, taxa_percentual)
                    VALUES (?, ?, ?, ?)
                """, (forma_pagamento.upper(), bandeira.upper(), parcelas, taxa))
                st.success("✅ Cadastro salvo com sucesso!")
                st.rerun()

    # Exibir tabela
    with sqlite3.connect(caminho_banco) as conn:
        df_taxas = pd.read_sql("""
            SELECT UPPER(forma_pagamento) AS 'Forma de Pagamento', 
                   UPPER(bandeira) AS 'Bandeira', 
                   parcelas AS 'Parcelas', 
                   taxa_percentual AS 'Taxa (%)'
            FROM taxas_maquinas
            WHERE NOT (forma_pagamento = 'DÉBITO' AND bandeira IN ('AMEX', 'DINERSCLUB'))
            ORDER BY forma_pagamento, bandeira, parcelas
        """, conn)

    if not df_taxas.empty:
        df_taxas["Taxa (%)"] = df_taxas["Taxa (%)"].apply(lambda x: f"{x:.2f}%")
        st.markdown("### 📋 Taxas Cadastradas:")
        st.dataframe(df_taxas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cadastro encontrado.")

# === Página de Usuários ============================================================================================
if st.session_state.get("mostrar_usuarios", False):
    st.subheader("👥 Cadastro de Usuários")

    with st.form("form_usuarios"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome Completo", max_chars=100)
            perfil = st.selectbox("Perfil", ["Administrador", "Gerente", "Vendedor"])
        
        with col2:
            email = st.text_input("Email", max_chars=100)
            ativo = st.selectbox("Usuário Ativo?", ["Sim", "Não"])

        senha = st.text_input("Senha", type="password", max_chars=50)
        confirmar_senha = st.text_input("Confirmar Senha", type="password", max_chars=50)

        submitted = st.form_submit_button("💾 Salvar Usuário")

        if submitted:
            if not nome or not email or not senha or not confirmar_senha:
                st.error("❗ Todos os campos são obrigatórios!")

            elif senha != confirmar_senha:
                st.warning("⚠️ As senhas não coincidem. Tente novamente.")

            elif not senha_forte(senha):
                st.warning("⚠️ A senha deve ter pelo menos 8 caracteres, com letra maiúscula, minúscula, número e símbolo.")

            elif "@" not in email or "." not in email:
                st.warning("⚠️ Digite um e-mail válido.")

            else:
                senha_hash = gerar_hash_senha(senha)
                ativo_valor = 1 if ativo == "Sim" else 0
                try:
                    with sqlite3.connect(caminho_banco) as conn:
                        conn.execute("""
                            INSERT INTO usuarios (nome, email, senha, perfil, ativo)
                            VALUES (?, ?, ?, ?, ?)
                        """, (nome, email, senha_hash, perfil, ativo_valor))
                        conn.commit()
                    st.success("✅ Usuário cadastrado com sucesso!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("⚠️ Email já cadastrado!")
                except Exception as e:
                    st.error(f"❌ Erro ao salvar usuário: {e}")

    # Exibir tabela de usuários com botões de ação
    st.markdown("### 📋 Usuários Cadastrados:")

    with sqlite3.connect(caminho_banco) as conn:
        df_usuarios = pd.read_sql("SELECT id, nome, email, perfil, ativo FROM usuarios", conn)

    if not df_usuarios.empty:
        for _, row in df_usuarios.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 2])
            
            with col1:
                st.write(f"👤 {row['nome']}")
            with col2:
                st.write(row["email"])
            with col3:
                status_text = "🟢 Ativo" if row["ativo"] == 1 else "🔴 Inativo"
                st.write(status_text)
            with col4:
                if st.button("🔁 ON/OFF", key=f"ativar_{row['id']}"):
                    novo_status = 0 if row["ativo"] == 1 else 1
                    with sqlite3.connect(caminho_banco) as conn:
                        conn.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (novo_status, row["id"]))
                        conn.commit()
                    st.rerun()
            with col5:
                if st.button("🗑️ Excluir", key=f"excluir_{row['id']}"):
                    if st.session_state.usuario_logado["email"] == row["email"]:
                        st.warning("⚠️ Você não pode excluir seu próprio usuário enquanto estiver logado.")
                    else:
                        with sqlite3.connect(caminho_banco) as conn:
                            conn.execute("DELETE FROM usuarios WHERE id = ?", (row["id"],))
                            conn.commit()
                        st.success(f"✅ Usuário '{row['nome']}' excluído.")
                        st.rerun()
    else:
        st.info("ℹ️ Nenhum usuário cadastrado.")

# === Página: Correção de Caixa ========================================================================================
if st.session_state.get("mostrar_correcao_caixa", False):
    st.subheader("🛠️ Correção Manual de Caixa")

    data_corrigir = st.date_input("Data do Ajuste", value=date.today())
    valor_ajuste = st.number_input("Valor de Correção (positivo ou negativo)", step=10.0, format="%.2f")
    observacao = st.text_input("Motivo ou Observação", max_chars=200)

    if st.button("💾 Salvar Ajuste Manual"):
        try:
            with sqlite3.connect(caminho_banco) as conn:
                conn.execute("""
                    INSERT INTO correcao_caixa (data, valor, observacao)
                    VALUES (?, ?, ?)
                """, (str(data_corrigir), valor_ajuste, observacao))
                conn.commit()
            st.success("✅ Ajuste salvo com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar correção: {e}")

    st.markdown("### 📋 Ajustes Registrados")
    try:
        with sqlite3.connect(caminho_banco) as conn:
            df_ajustes = pd.read_sql("SELECT * FROM correcao_caixa ORDER BY data DESC", conn)
        if not df_ajustes.empty:
            df_ajustes["valor"] = df_ajustes["valor"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            st.dataframe(df_ajustes, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum ajuste registrado ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar correções: {e}")