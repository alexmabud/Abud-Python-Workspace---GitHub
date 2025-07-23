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

# === Função para calcular o valor líquido de vendas em cartão =========================================================
def calcular_valor_liquido_cartao(df_entrada, data_base):
    """
    Filtra vendas em cartão do último dia útil anterior à data_base e calcula o valor líquido
    com base nas taxas cadastradas.
    """
    cal = BrazilDistritoFederal()
    data_util = ultimo_dia_util(data_base)

    # Filtra entradas do último dia útil com cartão
    df_cartao = df_entrada[
        (df_entrada["Data"].dt.date == data_util) &
        (df_entrada["Forma_de_Pagamento"].str.upper().isin(["CRÉDITO", "CREDITO", "DÉBITO", "DEBITO"]))
    ].copy()

    if df_cartao.empty:
        return 0.0

    # Normaliza as colunas para facilitar comparação com tabela de taxas
    df_cartao["forma"] = df_cartao["Forma_de_Pagamento"].str.upper()
    df_cartao["bandeira"] = df_cartao["Bandeira"].str.upper()
    df_cartao["parcelas"] = pd.to_numeric(df_cartao["Parcelas"], errors="coerce").fillna(1).astype(int)

    # Conecta ao banco para pegar as taxas
    with sqlite3.connect(caminho_banco) as conn:
        df_taxas = pd.read_sql("SELECT * FROM taxas_maquinas", conn)

    if df_taxas.empty:
        st.warning("⚠️ Nenhuma taxa de máquina cadastrada. Valor bruto será considerado.")
        return df_cartao["Valor"].sum()

    # Normaliza taxas
    df_taxas["forma_pagamento"] = df_taxas["forma_pagamento"].str.upper()
    df_taxas["bandeira"] = df_taxas["bandeira"].str.upper()

    # Merge das entradas com as taxas
    df_merge = pd.merge(
        df_cartao,
        df_taxas,
        how="left",
        left_on=["forma", "bandeira", "parcelas"],
        right_on=["forma_pagamento", "bandeira", "parcelas"]
    )

    # Aplica taxa (caso não tenha taxa cadastrada, assume 0%)
    df_merge["taxa_percentual"] = df_merge["taxa_percentual"].fillna(0)
    df_merge["valor_liquido"] = df_merge["Valor"] * (1 - df_merge["taxa_percentual"] / 100)

    return df_merge["valor_liquido"].sum()

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

    # === Carrega último fechamento salvo antes da data atual ===
    def buscar_saldo_anterior(data_base):
        with sqlite3.connect(caminho_banco) as conn:
            df = pd.read_sql("SELECT * FROM fechamento_caixa WHERE data < ? ORDER BY data DESC LIMIT 1", conn, params=(str(data_base),))
        if df.empty:
            return 0.0, 0.0, 0.0, 0.0, 0.0
        return (
            df.iloc[0]["banco_1"],
            df.iloc[0]["banco_2"],
            df.iloc[0]["banco_4"],
            df.iloc[0]["caixa"],
            df.iloc[0]["caixa2"]
        )

    saldo_ant_banco1, saldo_ant_banco2, saldo_ant_banco4, saldo_ant_caixa, saldo_ant_caixa2 = buscar_saldo_anterior(data_fechamento)

    # === Carrega entradas confirmadas ===
    df_entrada = carregar_tabela("entrada")
    df_entrada["Data"] = pd.to_datetime(df_entrada["Data"], errors="coerce")

    # Valores separados por forma de pagamento
    valor_pix = df_entrada[
        (df_entrada["Forma_de_Pagamento"].str.upper() == "PIX") &
        (df_entrada["Data"].dt.date == data_fechamento)
    ]["Valor"].sum()

    total_cartao_liquido = calcular_valor_liquido_cartao(df_entrada, data_fechamento)
    valor_banco_1 = valor_pix + total_cartao_liquido

    valor_dinheiro = df_entrada[
        (df_entrada["Forma_de_Pagamento"].str.upper() == "DINHEIRO") &
        (df_entrada["Data"].dt.date == data_fechamento)
    ]["Valor"].sum()

    # Calcula valor líquido das entradas via cartão do último dia útil
    def calcular_valor_liquido_cartao(df_entrada, data_base):
        cal = BrazilDistritoFederal()
        data_util = ultimo_dia_util(data_base)

        df_cartao = df_entrada[
            (df_entrada["Data"].dt.date == data_util) &
            (df_entrada["Forma_de_Pagamento"].str.upper().isin(["CRÉDITO", "CREDITO", "DÉBITO", "DEBITO"]))
        ].copy()

        if df_cartao.empty:
            return 0.0

        df_cartao["forma"] = df_cartao["Forma_de_Pagamento"].str.upper()
        df_cartao["bandeira"] = df_cartao["Bandeira"].str.upper()
        df_cartao["parcelas"] = pd.to_numeric(df_cartao["Parcelas"], errors="coerce").fillna(1).astype(int)

        with sqlite3.connect(caminho_banco) as conn:
            df_taxas = pd.read_sql("SELECT * FROM taxas_maquinas", conn)

        if df_taxas.empty:
            st.warning("⚠️ Nenhuma taxa cadastrada. Valor bruto será usado.")
            return df_cartao["Valor"].sum()

        df_taxas["forma_pagamento"] = df_taxas["forma_pagamento"].str.upper()
        df_taxas["bandeira"] = df_taxas["bandeira"].str.upper()

        df_merge = pd.merge(
            df_cartao,
            df_taxas,
            how="left",
            left_on=["forma", "bandeira", "parcelas"],
            right_on=["forma_pagamento", "bandeira", "parcelas"]
        )

        df_merge["taxa_percentual"] = df_merge["taxa_percentual"].fillna(0)
        df_merge["valor_liquido"] = df_merge["Valor"] * (1 - df_merge["taxa_percentual"] / 100)

        return df_merge["valor_liquido"].sum()

    total_cartao_liquido = calcular_valor_liquido_cartao(df_entrada, data_fechamento)

    # Sugestão automática (caso queira usar futuramente)
    sugerido_banco_1 = saldo_ant_banco1 + total_cartao_liquido

    # === Inputs visuais (Pix e Dinheiro bloqueados pois automáticos) ===
    col1, col2, col3 = st.columns(3)
    with col1:
        banco_1 = st.number_input("Saldo Banco 1 (Pix hoje + Cartões D-1 útil)", value=float(valor_banco_1), disabled=True, format="%.2f")
    with col2:
        banco_2 = st.number_input("Saldo Banco 2", min_value=0.0, step=10.0, value=saldo_ant_banco2)
    with col3:
        banco_4 = st.number_input("Saldo Banco 4", min_value=0.0, step=10.0, value=saldo_ant_banco4)

    col4, col5 = st.columns(2)
    with col4:
        caixa = st.number_input("Caixa Loja (Dinheiro)", value=float(valor_dinheiro), disabled=True, format="%.2f")
    with col5:
        caixa2 = st.number_input("Caixa 2 (dinheiro que levou pra casa)", min_value=0.0, step=10.0, value=saldo_ant_caixa2)

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
    total_pix_dinheiro = valor_pix + valor_dinheiro
    total_entradas = total_pix_dinheiro + total_cartao_liquido
    saldo_esperado = total_entradas - total_saidas + total_correcao

    # === Valor informado real (somado pelos campos digitados)
    valor_informado = (valor_pix + total_cartao_liquido) + banco_2 + banco_4 + caixa + caixa2
    diferenca = valor_informado - saldo_esperado

    # === Exibição do Resumo ===
    st.markdown("### 📈 Resumo do Fechamento do Dia")

    st.markdown("#### 📅 Detalhamento das Entradas")
    st.markdown(f"- 💸 Pix/Dinheiro de hoje: R$ {total_pix_dinheiro:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(f"- 💳 Cartão (líquido, do último dia útil): R$ {total_cartao_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"Entradas confirmadas: R$ {total_entradas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col2:
        st.error(f"Saídas: R$ {total_saidas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col3:
        st.success(f"Correções: R$ {total_correcao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown(f"### 💰 Saldo Esperado: R$ {saldo_esperado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.markdown(f"### 💵 Valor Informado: R$ {valor_informado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # === Validação antes de salvar ===
    if total_entradas <= 0 or valor_informado <= 0:
        st.warning("⚠️ Entradas e valor informado não podem ser zero.")
    else:
        if st.button("📅 Salvar Fechamento"):
            try:
                with sqlite3.connect(caminho_banco) as conn:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS fechamento_caixa (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT NOT NULL,
                            banco_1 REAL,
                            banco_2 REAL,
                            banco_3 REAL,
                            banco_4 REAL,
                            caixa REAL,
                            caixa_2 REAL,
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
                            data, banco_1, banco_2, banco_3, banco_4, caixa, caixa_2,
                            entradas_confirmadas, saidas, correcao, saldo_esperado, valor_informado, diferenca
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(data_fechamento),
                        float(valor_banco_1),
                        banco_2,
                        0.0,  # valor temporário para banco_3
                        banco_4,
                        float(valor_dinheiro),
                        caixa2,
                        total_entradas,
                        total_saidas,
                        total_correcao,
                        saldo_esperado,
                        valor_informado,
                        diferenca
                    ))
                    conn.commit()
                st.success("✅ Fechamento salvo com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# === Tabela de Fechamentos Recentes ===================================================================
    st.markdown("### 📋 Fechamentos Anteriores")

    try:
        with sqlite3.connect(caminho_banco) as conn:
            df_fechamentos = pd.read_sql(
                "SELECT * FROM fechamento_caixa ORDER BY data DESC LIMIT 15", conn
            )

        if not df_fechamentos.empty:
            df_fechamentos["data"] = pd.to_datetime(df_fechamentos["data"]).dt.strftime("%d/%m/%Y")

            colunas_exibir = [
                "data", "banco_1", "banco_2", "banco_3", "banco_4",
                "caixa", "caixa_2", "entradas_confirmadas", "saidas",
                "correcao", "saldo_esperado", "valor_informado", "diferenca"
            ]
            df_fechamentos = df_fechamentos[colunas_exibir].copy()

            # Formatar valores em R$
            for col in colunas_exibir[1:]:
                df_fechamentos[col] = df_fechamentos[col].apply(
                    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )

            st.dataframe(df_fechamentos, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum fechamento registrado ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar fechamentos anteriores: {e}")



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
    st.markdown("## 📝 Lançamentos do Dia")

# === Resumo do Lançamento do Dia ===================================================================================
    df_entrada = carregar_tabela("entrada")

    if not df_entrada.empty:
        df_entrada["Data"] = pd.to_datetime(df_entrada["Data"], errors="coerce")
        entradas_hoje = df_entrada[df_entrada["Data"].dt.date == date.today()]
        total_hoje = entradas_hoje["Valor"].sum()

        st.success(f"💰 Total de Entradas de hoje ({date.today().strftime('%d/%m/%Y')}): R$ {total_hoje:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        st.info("Ainda não há entradas registradas hoje.")

# === Resumo das Saídas do Dia =======================================================================================
    df_saida = carregar_tabela("saida")

    if not df_saida.empty:
        df_saida["Data"] = pd.to_datetime(df_saida["Data"], errors="coerce")
        saidas_hoje = df_saida[df_saida["Data"].dt.date == date.today()]
        total_saidas_hoje = saidas_hoje["Valor"].sum()

        st.error(f"📤 Total de Saídas de hoje ({date.today().strftime('%d/%m/%Y')}): R$ {total_saidas_hoje:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    else:
        st.info("Ainda não há saídas registradas hoje.")
    
    # === Campos de cadastro de entrada e saída ========================================================================
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 📅 Data do Lançamento")
    with col2:
        data_lancamento = st.date_input("", value=date.today())
    st.success("### 💼 Cadastrar Entrada")
    valor_entrada = st.number_input("Valor", min_value=0.0, step=0.01, key="valor_entrada")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["DINHEIRO", "PIX", "DÉBITO", "CRÉDITO"], key="forma_pagamento")

    # === Definir campos condicionalmente ===
    parcelas = 1
    bandeira = ""

    if forma_pagamento == "CRÉDITO":
        parcelas = st.selectbox("Parcelas", list(range(1, 13)), key="parcelas")
        bandeira = st.selectbox("Bandeira do Cartão (Crédito)", ["VISA", "MASTERCARD", "ELO", "AMEX", "DINERS CLUBE"], key="bandeira_credito")

    elif forma_pagamento == "DÉBITO":
        bandeira = st.selectbox("Bandeira do Cartão (Débito)", ["VISA", "MASTERCARD", "ELO"], key="bandeira_debito")

    # === Cadastro de Entrada ===
    confirmar = False
    if valor_entrada > 0:
        resumo = f"Valor: R$ {valor_entrada:.2f}, Forma: {forma_pagamento}, Parcelas: {parcelas}, Bandeira: {bandeira if bandeira else 'N/A'}"
        st.info(f"✅ Confirme os dados da entrada: → {resumo}")
        confirmar = st.checkbox("Está tudo certo com os dados acima?")

    with st.form("form_entrada"):
        submitted_entrada = st.form_submit_button("Salvar Entrada")

        if submitted_entrada and confirmar:
            if valor_entrada <= 0:
                st.warning("⚠️ O valor deve ser maior que zero.")
            else:
                try:
                    with sqlite3.connect(caminho_banco) as conn:
                        conn.execute("""
                            INSERT INTO entrada (Data, Valor, Forma_de_Pagamento, Parcelas, Bandeira)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            str(data_lancamento),
                            float(valor_entrada),
                            str(forma_pagamento).upper(),
                            int(parcelas),
                            str(bandeira).upper()
                        ))
                        conn.commit()
                    st.success(f"✅ Entrada cadastrada com sucesso! → Valor: R$ {valor_entrada:.2f}, Forma: {forma_pagamento}, Parcelas: {parcelas}, Bandeira: {bandeira if bandeira else 'N/A'}")
                except Exception as e:
                    st.error(f"Erro ao salvar entrada: {e}")
    
    # === Cadastro de Saída ==============================================================================================
    st.error("### 📤 Cadastrar Saída")

    # Campos de entrada para saída
    valor_saida = st.number_input("Valor da Saída", min_value=0.0, step=0.01, key="valor_saida")
    forma_pagamento_saida = st.selectbox("Forma de Pagamento", ["DINHEIRO", "PIX", "DÉBITO", "CRÉDITO"], key="forma_pagamento_saida")

    parcelas_saida = 1
    if forma_pagamento_saida == "CRÉDITO":
        parcelas_saida = st.selectbox("Parcelas", list(range(1, 13)), key="parcelas_saida")

    categoria_saida = st.text_input("Categoria")
    subcategoria_saida = st.text_input("Subcategoria")
    descricao_saida = st.text_input("Descricao")

    # Confirmação visual
    confirmar_saida = False
    if valor_saida > 0:
        resumo_saida = (
            f"Valor: R$ {valor_saida:.2f}, Forma: {forma_pagamento_saida}, Parcelas: {parcelas_saida}, "
            f"Categoria: {categoria_saida}, Subcategoria: {subcategoria_saida}, Descrição: {descricao_saida}"
        )
        st.info(f"✅ Confirme os dados da saída: → {resumo_saida}")
        confirmar_saida = st.checkbox("Está tudo certo com os dados acima?", key="confirmar_saida")

    # Botão de envio
    with st.form("form_saida"):
        submitted_saida = st.form_submit_button("Salvar Saída")

        if submitted_saida and confirmar_saida:
            try:
                with sqlite3.connect(caminho_banco) as conn:
                    conn.execute("""
                        INSERT INTO saida (
                            Data, Valor, Forma_de_Pagamento, Parcelas, Categoria, Sub_Categoria, Descricao
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(data_lancamento),
                        valor_saida,
                        forma_pagamento_saida.upper(),
                        parcelas_saida,
                        categoria_saida,
                        subcategoria_saida,
                        descricao_saida
                    ))
                    conn.commit()
                st.success("✅ Saída cadastrada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar saída: {e}")

    # === Cadastro de Compras ============================================================================================
    st.markdown("### 🧾 Cadastrar Compra")

    forma_pagamento_compra = st.selectbox("Forma de Pagamento da Compra", ["DINHEIRO", "PIX", "DÉBITO", "CRÉDITO"])
    valor_compra = st.number_input("Valor da Compra", min_value=0.0, step=0.01)
    categoria_compra = st.text_input("Categoria da Compra")
    subcategoria_compra = st.text_input("Subcategoria da Compra")
    descricao_compra = st.text_input("Descrição da Compra")
    parcelas_compra = 1

    if forma_pagamento_compra == "CRÉDITO":
        parcelas_compra = st.selectbox("Número de Parcelas", list(range(1, 13)), index=0)

    # === Exibir resumo antes do botão
    confirmar_compra = False
    if valor_compra > 0:
        resumo_compra = (
            f"Valor: R$ {valor_compra:.2f}, Forma: {forma_pagamento_compra}, Parcelas: {parcelas_compra}, "
            f"Categoria: {categoria_compra}, Subcategoria: {subcategoria_compra}, Descrição: {descricao_compra}"
        )
        st.info(f"✅ Confirme os dados da compra: → {resumo_compra}")
        confirmar_compra = st.checkbox("Está tudo certo com os dados acima?", key="confirmar_compra")

    # === Botão de envio fora de st.form (evita erro de formulário aninhado)
    botao_compra = st.button("Salvar Compra")

    if botao_compra and confirmar_compra:
        try:
            with sqlite3.connect(caminho_banco) as conn:
                if forma_pagamento_compra == "CRÉDITO":
                    conn.execute("""
                        INSERT INTO compras (data, valor, forma_pagamento, parcela, categoria, subcategoria, descricao)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(data_lancamento),
                        valor_compra,
                        forma_pagamento_compra,
                        parcelas_compra,
                        categoria_compra,
                        subcategoria_compra,
                        descricao_compra
                    ))

                    valor_parcela = valor_compra / parcelas_compra
                    for i in range(parcelas_compra):
                        vencimento = (pd.to_datetime(data_lancamento) + pd.DateOffset(months=i)).date()
                        descricao_parcela = f"{descricao_compra} (Parcela {i+1}/{parcelas_compra})"
                        conn.execute("""
                            INSERT INTO contas_a_pagar (data, valor, descricao)
                            VALUES (?, ?, ?)
                        """, (
                            str(vencimento),
                            valor_parcela,
                            descricao_parcela
                        ))
                else:
                    conn.execute("""
                        INSERT INTO saida (
                            Data, Valor, Forma_de_Pagamento, Parcelas,
                            Categoria, Sub_Categoria, Descricao
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(data_lancamento),
                        valor_compra,
                        forma_pagamento_compra,
                        1,
                        categoria_compra,
                        subcategoria_compra,
                        descricao_compra
                    ))
                conn.commit()
            st.success("✅ Compra registrada com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar compra: {e}")

    # === Cadastro de Mercadoria ===
    st.markdown("### 📦 Cadastrar Mercadoria")
    with st.form("form_mercadoria"):
        colecao = st.text_input("Coleção")
        fornecedor = st.text_input("Fornecedor")
        valor_mercadoria = st.number_input("Valor das Mercadorias", min_value=0.0, step=0.01)
        frete = st.number_input("Frete", min_value=0.0, step=0.01)
        previsao_faturamento = st.number_input("Previsão de Faturamento", min_value=0.0, step=0.01)
        faturamento = st.number_input("Faturamento", min_value=0.0, step=0.01)
        previsao_recebimento = st.number_input("Previsão de Recebimento", min_value=0.0, step=0.01)
        recebimento = st.number_input("Recebimento", min_value=0.0, step=0.01)
        pedido = st.text_input("Número do Pedido")
        nota_fiscal = st.text_input("Número da Nota Fiscal")
        submitted_mercadoria = st.form_submit_button("Salvar Mercadoria")

        if submitted_mercadoria:
            try:
                with sqlite3.connect(caminho_banco) as conn:
                    conn.execute("""
                        INSERT INTO mercadorias (
                            Data, Colecao, Fornecedor, Valor_Mercadoria, Frete,
                            Previsao_Faturamento, Faturamento, Previsao_Recebimento, Recebimento,
                            Pedido, Nota_Fiscal)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (str(data_lancamento), colecao, fornecedor, valor_mercadoria, frete,
                          previsao_faturamento, faturamento, previsao_recebimento, recebimento,
                          pedido, nota_fiscal))
                    conn.commit()
                st.success("✅ Mercadoria cadastrada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar mercadoria: {e}")

    # === Resumo do Dia (Entradas, Saídas, Mercadorias) ===
    st.markdown("## 📊 Resumo do Dia")

    filtro_data = data_lancamento

    try:
        df_entrada = carregar_tabela("entrada")
        df_entrada["Data"] = pd.to_datetime(df_entrada["Data"], errors="coerce")
        entradas_dia = df_entrada[df_entrada["Data"].dt.date == filtro_data]

        st.markdown("### 💸 Entradas do Dia")
        if entradas_dia.empty:
            st.info("Nenhuma entrada registrada para esse dia.")
        else:
            st.dataframe(entradas_dia[["Data", "Forma_de_Pagamento", "Valor", "Parcelas", "Bandeira",]], use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar entradas: {e}")

    try:
        df_saida = carregar_tabela("saida")
        df_saida["Data"] = pd.to_datetime(df_saida["Data"], errors="coerce")
        saidas_dia = df_saida[df_saida["Data"].dt.date == filtro_data]

        st.markdown("### 💼 Saídas do Dia")
        if saidas_dia.empty:
            st.info("Nenhuma saída registrada para esse dia.")
        else:
            st.dataframe(saidas_dia[["Data", "Categoria", "Valor", "Descricao"]], use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar saídas: {e}")

    try:
        df_compras = carregar_tabela("compras")
        df_compras["data"] = pd.to_datetime(df_compras["data"], errors="coerce")
        compras_dia = df_compras[df_compras["data"].dt.date == filtro_data]

        st.markdown("### 🧾 Compras do Dia")
        if compras_dia.empty:
            st.info("Nenhuma compra registrada para esse dia.")
        else:
            df_mostrar = compras_dia[[
                "data", "valor", "forma_pagamento", "parcela", "categoria", "subcategoria", "descricao"
            ]].copy()
            df_mostrar["valor"] = df_mostrar["valor"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            df_mostrar["data"] = df_mostrar["data"].dt.strftime("%d/%m/%Y")
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar compras: {e}")

    try:
        df_mercadoria = carregar_tabela("mercadorias")
        df_mercadoria["Data"] = pd.to_datetime(df_mercadoria["Data"], errors="coerce")
        mercadorias_dia = df_mercadoria[df_mercadoria["Data"].dt.date == filtro_data]

        st.markdown("### 📦 Mercadorias do Dia")
        if mercadorias_dia.empty:
            st.info("Nenhuma mercadoria registrada para esse dia.")
        else:
            st.dataframe(mercadorias_dia[[
                "Data", "Colecao", "Fornecedor", "Valor_Mercadoria", "Frete",
                "Previsao_Faturamento", "Faturamento", "Previsao_Recebimento", "Recebimento",
                "Pedido", "Nota_Fiscal"]], use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar mercadorias: {e}")

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