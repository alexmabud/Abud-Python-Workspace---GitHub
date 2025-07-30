import streamlit as st
import sqlite3
import os
import hashlib
import pandas as pd
import re
from datetime import date
from workalendar.america import BrazilDistritoFederal
from datetime import timedelta
import plotly.graph_objects as go

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
        "mostrar_fechamento_caixa", "mostrar_correcao_caixa","mostrar_cadastrar_cartao", "mostrar_saldos_bancarios", 
        "mostrar_cadastro_caixa", "mostrar_cadastro_meta"
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

# === Função: Cálculo do valor líquido das vendas em cartão ========================================================
def calcular_valor_liquido_cartao(df_entrada, data_base):
    dias_para_considerar = []
    dia_anterior = data_base - timedelta(days=1)

    while not cal.is_working_day(dia_anterior):
        dias_para_considerar.append(dia_anterior)
        dia_anterior -= timedelta(days=1)

    dias_para_considerar.append(dia_anterior)

    df_cartao = df_entrada[
        (df_entrada["Forma_de_Pagamento"].str.upper().isin(["DÉBITO", "CRÉDITO"])) &
        (df_entrada["Data"].dt.date.isin([d for d in dias_para_considerar]))
    ]

    total_liquido = 0.0

    mapeamento_bandeiras = {
        "MASTERCARD": "MASTER",
        "MASTER": "MASTER",
        "DINERS CLUB": "DINERSCLUB",
        "DINERSCLUB": "DINERSCLUB",
        "DINERS": "DINERSCLUB",
        "AMEX": "AMEX",
        "ELO": "ELO",
        "VISA": "VISA"
    }

    bandeira = mapeamento_bandeiras.get(bandeira, bandeira)  # Corrige o nome antes de consultar o banco

    for _, row in df_cartao.iterrows():
        valor = row["Valor"]
        forma = row["Forma_de_Pagamento"].upper().strip()
        bandeira_input = str(row.get("Bandeira", "")).upper().strip()
        parcelas = int(row.get("Parcelas", 1))

        # Aplica o mapeamento, se existir
        bandeira = mapeamento_bandeiras.get(bandeira_input, bandeira_input)

        with sqlite3.connect(caminho_banco) as conn:
            cursor = conn.execute("""
                SELECT taxa_percentual
                FROM taxas_maquinas
                WHERE UPPER(forma_pagamento) = ? 
                AND UPPER(bandeira) = ? 
                AND parcelas = ?
            """, (forma, bandeira, parcelas))
            resultado = cursor.fetchone()

        taxa = resultado[0] if resultado else 0.0
        valor_liquido = valor * (1 - taxa / 100)
        total_liquido += valor_liquido

    return round(total_liquido, 2)

# === Função para carregar cartões de crédito (com fechamento) ===
def carregar_cartoes_credito():
    with sqlite3.connect(caminho_banco) as conn:
        return pd.read_sql("SELECT * FROM cartoes_credito", conn)

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

# === Função para adicionar coluna de dia da semana ao DataFrame ====================================================
def adicionar_dia_semana(df):
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Dia_Semana"] = df["Data"].dt.day_name()
    traducao = {
        "Monday": "segunda",
        "Tuesday": "terca",
        "Wednesday": "quarta",
        "Thursday": "quinta",
        "Friday": "sexta",
        "Saturday": "sabado",
        "Sunday": "domingo"
    }
    df["Dia_Semana"] = df["Dia_Semana"].map(traducao)
    return df

# === Função para gerar gráfico de meta percentual ==================================================================
def grafico_meta_percentual(titulo, percentual):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentual,
        number={'suffix': "%"},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titulo, 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, 50], 'color': "#FFCDD2"},
                {'range': [50, 80], 'color': "#FFF9C4"},
                {'range': [80, 100], 'color': "#C8E6C9"}
            ]
        }
    ))
    return fig

# === Funções auxiliares para página de Metas ======================================================================================
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def carregar_metas():
    with sqlite3.connect(caminho_banco) as conn:
        return pd.read_sql("SELECT * FROM metas", conn)

def calcular_percentual(valor, meta):
    return round((valor / meta * 100), 1) if meta else 0

def extrair_metas(metas, coluna_dia):
    meta_dia = metas[coluna_dia].max() if coluna_dia in metas else 0
    meta_semana = metas["semanal"].max() if "semanal" in metas else 0
    meta_mes = metas["mensal"].max() if "mensal" in metas else 0
    meta_ouro = metas["meta_ouro"].max() if "meta_ouro" in metas else 16000
    meta_prata = metas["meta_prata"].max() if "meta_prata" in metas else 14000
    meta_bronze = metas["meta_bronze"].max() if "meta_bronze" in metas else 12000
    return meta_dia, meta_semana, meta_mes, meta_ouro, meta_prata, meta_bronze

def gerar_gauge(valor, titulo, nivel, cor):
    return go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        number={'suffix': "%", 'font': {'size': 22}},
        title={'text': f"{titulo}<br><b>{nivel}</b>", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': cor},
            'steps': [{'range': [0, 100], 'color': "#ECEFF1"}]
        }
    ))

# Função que exibe um bloco visual de destaque (ex: vendas ou metas)
def bloco_destaque(titulo, itens):
    st.markdown(f"""
    <div style='border: 1px solid #444; border-radius: 10px; padding: 20px; background-color: #1c1c1c; margin-bottom: 20px;'>
        <h4 style='color: white;'>{titulo}</h4>
        <table style='width: 100%; margin-top: 15px;'>
            <tr>
                {''.join([
                    f"<td style='text-align: center; width: 32%;'>"
                    f"<div style='color: #ccc; font-weight: bold;'>{label}</div>"
                    f"<div style='font-size: 1.5rem; color: #00FFAA;'>{formatar_valor(valor) if isinstance(valor, (int, float)) else valor}</div>"
                    f"</td>"
                    for label, valor in itens
                ])}
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Função que Exibe o bloco visual das comissões dos usuários (Gerente/Admin vê todos, Vendedor vê só a dele)
def bloco_comissoes(df_entrada, df_metas, coluna_dia, usuario_logado, perfil_logado, caminho_banco):
    if perfil_logado in ["Administrador", "Gerente"]:
        usuarios = df_metas[df_metas["vendedor"].str.upper() != "LOJA"]["vendedor"].unique() if not df_metas.empty else []
    else:
        usuarios = [usuario_logado]

    html = """
    <div style='border: 1px solid #444; border-radius: 10px; padding: 20px; background-color: #1c1c1c; margin-bottom: 20px;'>
        <h4 style='color: white;'>💰 Comissões</h4>
    """
    for nome in usuarios:
        nome_upper = nome.upper()
        df_user = df_entrada[df_entrada["Usuario"].str.upper() == nome_upper]
        valor_mes = df_user[df_user["Data"].dt.date >= date.today().replace(day=1)]["Valor"].sum()
        with sqlite3.connect(caminho_banco) as conn:
            cursor = conn.execute("SELECT id FROM usuarios WHERE UPPER(nome) = ?", (nome_upper,))
            id_usuario = cursor.fetchone()
            metas_usuario = pd.read_sql("SELECT * FROM metas WHERE id_usuario = ?", conn, params=(id_usuario[0],)) if id_usuario else pd.DataFrame()
        _, _, _, ouro, prata, bronze = extrair_metas(metas_usuario, coluna_dia) if not metas_usuario.empty else (0,0,0,0,0,0)
        if valor_mes >= ouro:
            nivel, perc_comissao = "🥇 Ouro", 2.0
        elif valor_mes >= prata:
            nivel, perc_comissao = "🥈 Prata", 1.5
        elif valor_mes >= bronze:
            nivel, perc_comissao = "🥉 Bronze", 1.0
        else:
            nivel, perc_comissao = None, 0.0

        if nivel:
            valor_comissao = (valor_mes * perc_comissao) / 100
            msg = f"Comissão: <b>{perc_comissao:.1f}%</b> = <span style='color:#00FFAA'>{formatar_valor(valor_comissao)}</span>"
            if nome_upper == usuario_logado:
                html += f"<div style='color: #00FFAA; margin-bottom: 10px;'>✅ Você bateu a meta <b>{nivel}</b>. {msg}</div>"
            else:
                html += f"<div style='color: #ccc; margin-bottom: 10px;'>👤 <b>{nome}</b> bateu a meta <b>{nivel}</b> — {msg}</div>"
        elif nome_upper == usuario_logado:
            html += "<div style='color: orange; margin-bottom: 10px;'>⚠️ Você ainda não bateu a <b>meta do mês</b>.</div>"
        elif perfil_logado != "Vendedor":
            html += f"<div style='color: #888; margin-bottom: 10px;'>👤 <b>{nome}</b> ainda não bateu a meta do mês.</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# Função que Exibe os gráficos de metas para todos os perfis (Adm/Gerente veem todos, Vendedor vê só a loja e ele mesmo)
def graficos_vendedores(df_entrada, df_metas, coluna_dia, perfil_logado, usuario_logado, caminho_banco, hoje, inicio_semana, inicio_mes):
    usuarios_unicos = ["LOJA"] + sorted([u for u in df_entrada["Usuario"].unique() if u.upper() != "LOJA"])
    for i, vendedor in enumerate(usuarios_unicos):
        nome_upper = vendedor.upper()
        # Vendedor só vê a loja e ele mesmo
        if perfil_logado == "Vendedor" and nome_upper not in ["LOJA", usuario_logado]:
            continue

        if nome_upper == "LOJA":
            df_user = df_entrada.copy()
            metas = df_metas[df_metas["vendedor"].str.upper() == "LOJA"] if not df_metas.empty else pd.DataFrame()
        else:
            df_user = df_entrada[df_entrada["Usuario"].str.upper() == nome_upper]
            with sqlite3.connect(caminho_banco) as conn:
                cursor = conn.execute("SELECT id FROM usuarios WHERE UPPER(nome) = ?", (nome_upper,))
                id_usuario = cursor.fetchone()
                metas = pd.read_sql("SELECT * FROM metas WHERE id_usuario = ?", conn, params=(id_usuario[0],)) if id_usuario else pd.DataFrame()
        meta_dia, meta_semana, meta_mes, ouro, prata, bronze = extrair_metas(metas, coluna_dia) if not metas.empty else (0,0,0,0,0,0)
        valor_dia = df_user[df_user["Data"].dt.date == hoje]["Valor"].sum()
        valor_semana = df_user[df_user["Data"].dt.date >= inicio_semana]["Valor"].sum()
        valor_mes = df_user[df_user["Data"].dt.date >= inicio_mes]["Valor"].sum()
        perc_dia = calcular_percentual(valor_dia, meta_dia)
        perc_semana = calcular_percentual(valor_semana, meta_semana)
        perc_mes = calcular_percentual(valor_mes, meta_mes)
        nivel_atual, cor = "Nenhum", "#B0BEC5"
        if valor_mes >= ouro:
            nivel_atual, cor = "🥇 Ouro", "#FFD700"
        elif valor_mes >= prata:
            nivel_atual, cor = "🥈 Prata", "#C0C0C0"
        elif valor_mes >= bronze:
            nivel_atual, cor = "🥉 Bronze", "#CD7F32"

        if nome_upper == "LOJA":
            st.markdown(f"<h5 style='margin: 5px 0;'>🏪 LOJA</h5>", unsafe_allow_html=True)
            st.plotly_chart(grafico_meta_percentual("Meta do Dia", perc_dia), use_container_width=True, key="grafico_loja_dia")
            col1, col2, col3 = st.columns(3)
            col1.plotly_chart(grafico_meta_percentual("Meta da Semana", perc_semana), use_container_width=True, key="grafico_loja_semana")
            col2.plotly_chart(grafico_meta_percentual("Meta do Mês", perc_mes), use_container_width=True, key="grafico_loja_mes")
            col3.plotly_chart(gerar_gauge(perc_mes, "Nível da Meta", nivel_atual, cor), use_container_width=True, key="grafico_loja_nivel")
        else:
            st.markdown(f"<h5 style='margin: 5px 0 -25px;'>👤 {vendedor}</h5>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            col1.plotly_chart(grafico_meta_percentual("Meta do Dia", perc_dia), use_container_width=True, key=f"grafico_dia_{i}")
            col2.plotly_chart(grafico_meta_percentual("Meta da Semana", perc_semana), use_container_width=True, key=f"grafico_semana_{i}")
            col3.plotly_chart(grafico_meta_percentual("Meta do Mês", perc_mes), use_container_width=True, key=f"grafico_mes_{i}")
            col4.plotly_chart(gerar_gauge(perc_mes, "Nível da Meta", nivel_atual, cor), use_container_width=True, key=f"grafico_nivel_{i}")

# Funções de destaque para blocos de informações do Fechamento de Caixa ====================================================================================
def bloco_destaque_3(titulo, itens):
    st.markdown(f"""
    <div style='border: 1px solid #444; border-radius: 10px; padding: 20px; background-color: #1c1c1c; margin-bottom: 20px;'>
        <h4 style='color: white;'>{titulo}</h4>
        <table style='width: 100%; margin-top: 15px; table-layout: fixed;'>
            <tr>
                {''.join([
                    f"<td style='text-align: center; width: 33%;'>"
                    f"<div style='color: #ccc; font-weight: bold;'>{label}</div>"
                    f"<div style='font-size: 1.3rem; color: #00FFAA;'>{valor}</div>"
                    f"</td>"
                    for label, valor in itens
                ])}
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Função de destaque para 2 colunas (Caixa)
def bloco_destaque_2(titulo, label1, valor1, label2, valor2):
    st.markdown(f"""
    <div style='border: 1px solid #444; border-radius: 10px; padding: 20px; background-color: #1c1c1c; margin-bottom: 20px;'>
        <h4 style='color: white;'>{titulo}</h4>
        <table style='width: 100%; margin-top: 15px; table-layout: fixed;'>
            <tr>
                <td style='text-align: center; width: 50%;'>
                    <div style='color: #ccc; font-weight: bold;'>{label1}</div>
                    <div style='font-size: 1.5rem; color: #00FFAA;'>{valor1}</div>
                </td>
                <td style='text-align: center; width: 50%;'>
                    <div style='color: #ccc; font-weight: bold;'>{label2}</div>
                    <div style='font-size: 1.5rem; color: #00FFAA;'>{valor2}</div>
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Função de destaque para 4 colunas (Bancos)
def bloco_destaque_4(titulo, itens):
    st.markdown(f"""
    <div style='border: 1px solid #444; border-radius: 10px; padding: 20px; background-color: #1c1c1c; margin-bottom: 20px;'>
        <h4 style='color: white;'>{titulo}</h4>
        <table style='width: 100%; margin-top: 15px; table-layout: fixed;'>
            <tr>
                {''.join([
                    f"<td style='text-align: center; width: 25%;'>"
                    f"<div style='color: #ccc; font-weight: bold;'>{label}</div>"
                    f"<div style='font-size: 1.2rem; color: #00FFAA;'>{valor}</div>"
                    f"</td>"
                    for label, valor in itens
                ])}
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Função para saldo total centralizado com confirmação e botão
def bloco_saldo_total(titulo, saldo_total):
    col = st.columns([1, 2, 1])[1]  # Centraliza o bloco
    with col:
        st.markdown(f"""
        <div style='border: 2px solid #FFD700; border-radius: 15px; padding: 32px; background-color: #222; margin-bottom: 30px; text-align:center;'>
            <h2 style='color: #FFD700; font-size: 2.2rem; margin-bottom: 15px;'>{titulo}</h2>
            <div style='font-size: 2.4rem; color: #00FFAA; font-weight: bold; margin-bottom: 30px;'>
                R$ {saldo_total:,.2f}
            </div>
        """, unsafe_allow_html=True)
        confirmar = st.checkbox(
            f"Confirma saldo total: R$ {saldo_total:,.2f}".replace(".", ","),
            key="confirmar_fechamento"
        )
        salvar = st.button("💾 Salvar Fechamento", key="btn_salvar_fechamento")
        st.markdown("</div>", unsafe_allow_html=True)
    return confirmar, salvar

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
    "mostrar_cadastrar_cartao": False,
    "mostrar_saldos_bancarios": False,
    "mostrar_correcao_caixa": False,
    "mostrar_cadastro_meta": False,
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

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# === Submenu: Metas ================================================================================================
if opcao == "🎯 Metas":
    df_entrada = carregar_tabela("entrada")
    df_entrada = adicionar_dia_semana(df_entrada)
    df_entrada["Data"] = pd.to_datetime(df_entrada["Data"], errors="coerce")
    df_entrada["Usuario"] = df_entrada.get("Usuario", "LOJA").fillna("LOJA")

    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)
    dias_semana = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    coluna_dia = dias_semana[hoje.weekday()]

    df_metas = carregar_metas()

    # --- Vendas
    df_loja = df_entrada.copy()
    total_dia = df_loja[df_loja["Data"].dt.date == hoje]["Valor"].sum()
    total_semana = df_loja[df_loja["Data"].dt.date >= inicio_semana]["Valor"].sum()
    total_mes = df_loja[df_loja["Data"].dt.date >= inicio_mes]["Valor"].sum()
    bloco_destaque("🏪 Vendas da Loja", [
        ("Vendas do Dia", total_dia),
        ("Vendas da Semana", total_semana),
        ("Vendas do Mês", total_mes)
    ])

    # --- Metas
    metas_loja = df_metas[df_metas["vendedor"].str.upper() == "LOJA"] if not df_metas.empty else pd.DataFrame()
    meta_dia, meta_semana, meta_mes, _, _, _ = extrair_metas(metas_loja, coluna_dia) if not metas_loja.empty else (0,0,0,0,0,0)
    bloco_destaque("🎯 Metas da Loja", [
        ("Meta do Dia", meta_dia),
        ("Meta da Semana", meta_semana),
        ("Meta do Mês", meta_mes)
    ])

    # --- Comissões
    usuario_logado = st.session_state.usuario_logado.get("nome", "").upper()
    perfil_logado = st.session_state.usuario_logado.get("perfil", "")
    bloco_comissoes(df_entrada, df_metas, coluna_dia, usuario_logado, perfil_logado, caminho_banco)

    # --- Gráficos
    graficos_vendedores(df_entrada, df_metas, coluna_dia, perfil_logado, usuario_logado, caminho_banco, hoje, inicio_semana, inicio_mes)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



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

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# === Submenu: Fechamento de Caixa ==========================================================
if opcao == "💼 Fechamento de Caixa":
    data_fechamento = st.date_input("Data do Fechamento", value=date.today())
    st.markdown(f"🗓️ **Fechamento do dia:** {data_fechamento.strftime('%d/%m/%Y')}")
    data_fechamento_str = str(data_fechamento)
    data_util_anterior = ultimo_dia_util(data_fechamento)

    # Entradas
    df_entrada = carregar_tabela("entrada")
    df_entrada["Data"] = pd.to_datetime(df_entrada["Data"], errors="coerce")

    valor_dinheiro = df_entrada[
        (df_entrada["Forma_de_Pagamento"].str.upper() == "DINHEIRO") &
        (df_entrada["Data"].dt.date == data_fechamento)
    ]["Valor"].sum() or 0.0

    valor_pix = df_entrada[
        (df_entrada["Forma_de_Pagamento"].str.upper() == "PIX") &
        (df_entrada["Data"].dt.date == data_fechamento)
    ]["Valor"].sum() or 0.0

    # Atualiza/Grava caixa_vendas, caixa_total e caixa2_total para a data do fechamento
    with sqlite3.connect(caminho_banco) as conn:
        # Busca o valor manual já lançado no caixa para esse dia
        cursor = conn.execute("SELECT caixa, caixa_2 FROM saldos_caixas WHERE data = ?", (data_fechamento_str,))
        resultado_caixa = cursor.fetchone()
        caixa_manual = float(resultado_caixa[0]) if resultado_caixa else 0.0
        caixa2_manual = float(resultado_caixa[1]) if resultado_caixa else 0.0

        # Busca se já existe registro
        cursor = conn.execute("SELECT 1 FROM saldos_caixas WHERE data = ?", (data_fechamento_str,))
        existe = cursor.fetchone()
        if existe:
            conn.execute("""
                UPDATE saldos_caixas 
                SET caixa_vendas = ?, 
                    caixa_total = ?, 
                    caixa2_total = ?
                WHERE data = ?
            """, (
                valor_dinheiro, 
                caixa_manual + valor_dinheiro, 
                caixa2_manual,   # Atualize se houver transferência no mesmo dia
                data_fechamento_str
            ))
        else:
            conn.execute("""
                INSERT INTO saldos_caixas (data, caixa_vendas, caixa, caixa_total, caixa_2, caixa2_dia, caixa2_total)
                VALUES (?, ?, 0, ?, 0, 0, ?)
            """, (
                data_fechamento_str, 
                valor_dinheiro, 
                valor_dinheiro,     # caixa_total = caixa (zero) + caixa_vendas
                caixa2_manual       # caixa2_total
            ))
        conn.commit()

    # Busca saldos de caixa e caixa 2 (usar _total!)
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.execute("""
            SELECT caixa_total, caixa2_total
            FROM saldos_caixas
            WHERE data = ?
            LIMIT 1
        """, (data_fechamento_str,))
        resultado = cursor.fetchone()

    if resultado:
        valor_caixa = resultado[0] or 0.0
        valor_caixa2 = resultado[1] or 0.0
    else:
        st.warning("⚠️ Nenhum saldo encontrado em `saldos_caixas` para a data selecionada.")
        valor_caixa = 0.0
        valor_caixa2 = 0.0

    # Saldos dos bancos
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.execute("""
            SELECT banco_1, banco_2, banco_3, banco_4 
            FROM saldos_bancos 
            WHERE data <= ? 
            ORDER BY data DESC 
            LIMIT 1
        """, (data_fechamento_str,))
        resultado_bancos = cursor.fetchone()

        if resultado_bancos:
            saldo_cad_banco_1, saldo_cad_banco_2, saldo_cad_banco_3, saldo_cad_banco_4 = resultado_bancos
        else:
            saldo_cad_banco_1 = saldo_cad_banco_2 = saldo_cad_banco_3 = saldo_cad_banco_4 = 0.0

    def calcular_valor_liquido_cartao(df_entrada, data_base):
        cal = BrazilDistritoFederal()
        dias_para_considerar = []
        dia_anterior = data_base - timedelta(days=1)
        while not cal.is_working_day(dia_anterior):
            dias_para_considerar.append(dia_anterior)
            dia_anterior -= timedelta(days=1)
        dias_para_considerar.append(dia_anterior)
        df_cartao = df_entrada[
            (df_entrada["Forma_de_Pagamento"].str.upper().isin(["DÉBITO", "CRÉDITO"])) &
            (df_entrada["Data"].dt.date.isin([d for d in dias_para_considerar]))
        ]
        total_liquido = 0.0
        mapeamento_bandeiras = {
            "MASTERCARD": "MASTER",
            "MASTER": "MASTER",
            "DINERS CLUB": "DINERSCLUB",
            "DINERSCLUB": "DINERSCLUB",
            "DINERS": "DINERSCLUB",
            "DINERSCLUBE": "DINERSCLUB",
            "DINERSCLUBINTERNACIONAL": "DINERSCLUB",
            "AMEX": "AMEX",
            "ELO": "ELO",
            "VISA": "VISA"
        }
        for _, row in df_cartao.iterrows():
            valor = row["Valor"]
            forma = row["Forma_de_Pagamento"].upper()
            bandeira_raw = str(row.get("Bandeira", "")).upper().replace(" ", "").replace("-", "")
            bandeira = mapeamento_bandeiras.get(bandeira_raw, bandeira_raw)
            parcelas = int(row.get("Parcelas", 1))
            with sqlite3.connect(caminho_banco) as conn:
                cursor = conn.execute("""
                    SELECT taxa_percentual
                    FROM taxas_maquinas
                    WHERE UPPER(forma_pagamento) = ? 
                    AND UPPER(bandeira) = ? 
                    AND parcelas = ?
                """, (forma, bandeira, parcelas))
                resultado = cursor.fetchone()
            taxa = resultado[0] if resultado else 0.0
            valor_liquido = valor * (1 - taxa / 100)
            total_liquido += valor_liquido
        return round(total_liquido, 2)

    total_cartao_liquido = calcular_valor_liquido_cartao(df_entrada, data_fechamento)
    valor_banco_1 = saldo_cad_banco_1 + valor_pix + total_cartao_liquido

    # Bloco: Valores que Entraram Hoje
    bloco_destaque_3(
        "🪙 Valores que Entraram Hoje",
        [
            ("Dinheiro", f"R$ {valor_dinheiro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Pix", f"R$ {valor_pix:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Cartão D-1 (Líquido)", f"R$ {total_cartao_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        ]
    )

    # Saídas e correções
    df_saida = carregar_tabela("saida")
    df_saida["Data"] = pd.to_datetime(df_saida["Data"], errors="coerce")
    total_saidas = df_saida[df_saida["Data"].dt.date == data_fechamento]["Valor"].sum()
    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.execute("SELECT SUM(valor) FROM correcao_caixa WHERE data = ?", (data_fechamento_str,))
        total_correcao = cursor.fetchone()[0] or 0.0

    # Saldo total
    saldo_total = valor_caixa + valor_caixa2 + valor_banco_1 + saldo_cad_banco_2 + saldo_cad_banco_3 + saldo_cad_banco_4 + total_correcao

    # Bloco: Resumo das Movimentações de Hoje
    entradas_confirmadas = valor_pix + valor_dinheiro + total_cartao_liquido
    bloco_destaque_3(
        "🔁 Resumo das Movimentações de Hoje",
        [
            ("Entradas", f"R$ {entradas_confirmadas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Saídas", f"R$ {total_saidas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Correções", f"R$ {total_correcao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        ]
    )

    # Bloco: Saldo em Caixa
    bloco_destaque_2(
        "💵 Saldo em Caixa",
        "Caixa", f"R$ {valor_caixa:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "Caixa 2", f"R$ {valor_caixa2:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    # Bloco: Saldo em Bancos
    bloco_destaque_4(
        "🏦 Saldo em Bancos",
        [
            ("Inter", f"R$ {valor_banco_1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Bradesco", f"R$ {saldo_cad_banco_2:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("InfinitePay", f"R$ {saldo_cad_banco_3:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Outros Bancos", f"R$ {saldo_cad_banco_4:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        ]
    )

    # Bloco: Saldo Total central, já com checkbox e botão
    confirmar, salvar = bloco_saldo_total("💰 Saldo Total", saldo_total)

    if salvar:
        if not confirmar:
            st.warning("⚠️ Você precisa confirmar que o saldo está correto antes de salvar.")
        else:
            try:
                with sqlite3.connect(caminho_banco) as conn:
                    cursor = conn.execute("SELECT 1 FROM fechamento_caixa WHERE data = ?", (data_fechamento_str,))
                    if cursor.fetchone():
                        st.warning("⚠️ Já existe um fechamento salvo para esta data.")
                    else:
                        conn.execute("""
                            INSERT INTO fechamento_caixa (
                                data, banco_1, banco_2, banco_3, banco_4,
                                caixa, caixa_2, entradas_confirmadas, saidas,
                                correcao, saldo_esperado, valor_informado, diferenca
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(data_fechamento),
                            float(valor_banco_1),
                            saldo_cad_banco_2,
                            saldo_cad_banco_3,
                            saldo_cad_banco_4,
                            float(valor_caixa),
                            valor_caixa2,
                            valor_pix + valor_dinheiro + total_cartao_liquido,
                            total_saidas,
                            total_correcao,
                            saldo_total,
                            saldo_total,
                            0.0
                        ))
                        conn.commit()
                        st.success("✅ Fechamento salvo com sucesso!")
                        st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    # --- Tabela de Fechamentos Anteriores ---
    with sqlite3.connect(caminho_banco) as conn:
        df_fechamentos = pd.read_sql("""
            SELECT 
                data as 'Data',
                banco_1 as 'Inter',
                banco_2 as 'Bradesco',
                banco_3 as 'InfinitePay',
                banco_4 as 'Outros Bancos',
                caixa as 'Caixa',
                caixa_2 as 'Caixa 2',
                entradas_confirmadas as 'Entradas',
                saidas as 'Saídas',
                correcao as 'Correções',
                saldo_esperado as 'Saldo Esperado',
                valor_informado as 'Valor Informado',
                diferenca as 'Diferença'
            FROM fechamento_caixa
            ORDER BY data DESC
        """, conn)

    if not df_fechamentos.empty:
        st.markdown("### 📋 Fechamentos Anteriores")
        st.dataframe(df_fechamentos.style.format({
            "Inter": "R$ {:,.2f}",
            "Bradesco": "R$ {:,.2f}",
            "InfinitePay": "R$ {:,.2f}",
            "Outros Bancos": "R$ {:,.2f}",
            "Caixa": "R$ {:,.2f}",
            "Caixa 2": "R$ {:,.2f}",
            "Entradas": "R$ {:,.2f}",
            "Saídas": "R$ {:,.2f}",
            "Correções": "R$ {:,.2f}",
            "Saldo Esperado": "R$ {:,.2f}",
            "Valor Informado": "R$ {:,.2f}",
            "Diferença": "R$ {:,.2f}",
        }), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum fechamento realizado ainda.")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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

    if st.sidebar.button("📇 Cadastrar Cartão de Crédito"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_cadastrar_cartao = True

    if st.sidebar.button("🏦 Cadastrar Saldos Bancários"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_saldos_bancarios = True

    if st.sidebar.button("💵 Cadastro de Caixa"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_cadastro_caixa = True

    if st.sidebar.button("🎯 Cadastro de Metas"):
        limpar_todas_as_paginas()
        st.session_state.mostrar_cadastro_meta = True

# === Página: Lançamentos do Dia =====================================================================================
if st.session_state.get("mostrar_lancamentos_do_dia", False):
    st.markdown("## 📝 Lançamentos do Dia")
    
    # Define a data de lançamento para uso nos resumos e nos cadastros
    data_lancamento = st.date_input("📅 Data do Lançamento", value=date.today(), key="data_lancamento_input")
    filtro_data = data_lancamento



    # # === Cadastro de Entrada ========================================================================================
    # st.markdown("### 💼 Cadastrar Entrada")
    # valor_entrada = st.number_input("Valor", min_value=0.0, step=0.01, key="valor_entrada")
    # forma_pagamento = st.selectbox("Forma de Pagamento", ["DINHEIRO", "PIX", "DÉBITO", "CRÉDITO"], key="forma_pagamento")

    # # === Definir campos condicionalmente ===
    # parcelas = 1
    # bandeira = ""

    # if forma_pagamento == "CRÉDITO":
    #     parcelas = st.selectbox("Parcelas", list(range(1, 13)), key="parcelas")
    #     bandeira = st.selectbox("Bandeira do Cartão (Crédito)", ["VISA", "MASTERCARD", "ELO", "AMEX", "DINERS CLUBE"], key="bandeira_credito")

    # elif forma_pagamento == "DÉBITO":
    #     bandeira = st.selectbox("Bandeira do Cartão (Débito)", ["VISA", "MASTERCARD", "ELO"], key="bandeira_debito")

    # # === Cadastro de Entrada ===
    # confirmar = False
    # if valor_entrada > 0:
    #     resumo = f"Valor: R$ {valor_entrada:.2f}, Forma: {forma_pagamento}, Parcelas: {parcelas}, Bandeira: {bandeira if bandeira else 'N/A'}"
    #     st.info(f"✅ Confirme os dados da entrada: → {resumo}")
    #     confirmar = st.checkbox("Está tudo certo com os dados acima?")

    # with st.form("form_entrada"):
    #     submitted_entrada = st.form_submit_button("Salvar Entrada")

    #     if submitted_entrada and confirmar:
    #         if valor_entrada <= 0:
    #             st.warning("⚠️ O valor deve ser maior que zero.")
    #         else:
    #             try:
    #                 with sqlite3.connect(caminho_banco) as conn:
    #                     usuario = st.session_state.usuario_logado["nome"]  # ← nome de quem está logado

    #                     conn.execute("""
    #                         INSERT INTO entrada (Data, Valor, Forma_de_Pagamento, Parcelas, Bandeira, Usuario)
    #                         VALUES (?, ?, ?, ?, ?, ?)
    #                     """, (
    #                         str(data_lancamento),
    #                         float(valor_entrada),
    #                         str(forma_pagamento).upper(),
    #                         int(parcelas),
    #                         str(bandeira).upper(),
    #                         usuario
    #                     ))
    #                     conn.commit()

    #                 st.success(f"✅ Entrada cadastrada com sucesso! → Valor: R$ {valor_entrada:.2f}, Forma: {forma_pagamento}, Parcelas: {parcelas}, Bandeira: {bandeira if bandeira else 'N/A'}")
    #             except Exception as e:
    #                 st.error(f"Erro ao salvar entrada: {e}")























# # === Cadastro de Mercadoria ===
#         st.markdown("### 📦 Cadastrar Mercadoria")
#         with st.form("form_mercadoria"):
#             colecao = st.text_input("Coleção")
#             fornecedor = st.text_input("Fornecedor")
#             valor_mercadoria = st.number_input("Valor das Mercadorias", min_value=0.0, step=0.01)
#             frete = st.number_input("Frete", min_value=0.0, step=0.01)
#             previsao_faturamento = st.number_input("Previsão de Faturamento", min_value=0.0, step=0.01)
#             faturamento = st.number_input("Faturamento", min_value=0.0, step=0.01)
#             previsao_recebimento = st.number_input("Previsão de Recebimento", min_value=0.0, step=0.01)
#             recebimento = st.number_input("Recebimento", min_value=0.0, step=0.01)
#             pedido = st.text_input("Número do Pedido")
#             nota_fiscal = st.text_input("Número da Nota Fiscal")
#             submitted_mercadoria = st.form_submit_button("Salvar Mercadoria")

#             if submitted_mercadoria:
#                 try:
#                     with sqlite3.connect(caminho_banco) as conn:
#                         conn.execute("""
#                             INSERT INTO mercadorias (
#                                 Data, Colecao, Fornecedor, Valor_Mercadoria, Frete,
#                                 Previsao_Faturamento, Faturamento, Previsao_Recebimento, Recebimento,
#                                 Pedido, Nota_Fiscal)
#                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                         """, (
#                             str(data_lancamento), colecao, fornecedor, valor_mercadoria, frete,
#                             previsao_faturamento, faturamento, previsao_recebimento, recebimento,
#                             pedido, nota_fiscal
#                         ))
#                         conn.commit()
#                     st.success("✅ Mercadoria cadastrada com sucesso!")
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Erro ao salvar mercadoria: {e}")










    








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

# === Página: Ver Cartão de Crédito ==================================================================================
if st.session_state.get("mostrar_cartao_credito", False):
    st.subheader("💳 Cartões de Crédito Cadastrados")

    try:
        cartoes_df = carregar_cartoes_credito()
        if cartoes_df.empty:
            st.info("ℹ️ Nenhum cartão cadastrado ainda.")
        else:
            cartoes_df = cartoes_df.rename(columns={"nome": "Cartão", "fechamento": "Fechamento (dia)"})
            st.dataframe(cartoes_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar cartões: {e}")

# === Página: Contas a Pagar ========================================================================================
if st.session_state.get("mostrar_contas_pagar", False):
    st.subheader("📄 Contas a Pagar")
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

    # -- Inicializa estado de sucesso se não existir
    if "correcao_sucesso" not in st.session_state:
        st.session_state["correcao_sucesso"] = False

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
            st.session_state["correcao_sucesso"] = True
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar correção: {e}")

    # -- Mensagem de sucesso fixa até clicar em OK
    if st.session_state.get("correcao_sucesso", False):
        st.success("✅ Ajuste salvo com sucesso!")
        if st.button("OK, entendi!", key="ok_sucesso_correcao"):
            st.session_state["correcao_sucesso"] = False
            st.rerun()

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

# === Página: Cadastro de Cartões de Crédito =========================================================================
if st.session_state.get("mostrar_cadastrar_cartao", False) and st.session_state.get("pagina_atual") == "🛠️ Cadastro":
    st.subheader("📇 Cadastro de Cartões de Crédito")

    with st.form("form_cadastrar_cartao_credito"):
        nome_cartao = st.text_input("Nome do Cartão (Ex: Nubank, Inter, Bradesco)")
        fechamento = st.number_input("Dia do Fechamento da Fatura", min_value=1, max_value=31, step=1)
        submitted_cartao = st.form_submit_button("💾 Salvar Cartão")

        if submitted_cartao:
            if not nome_cartao:
                st.warning("⚠️ Informe o nome do cartão.")
            else:
                try:
                    with sqlite3.connect(caminho_banco) as conn:
                        conn.execute("""
                            CREATE TABLE IF NOT EXISTS cartoes_credito (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nome TEXT NOT NULL,
                                fechamento INTEGER NOT NULL
                            )
                        """)
                        conn.execute("""
                            INSERT INTO cartoes_credito (nome, fechamento)
                            VALUES (?, ?)
                        """, (nome_cartao, fechamento))
                        conn.commit()
                    st.success("✅ Cartão cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar cartão: {e}")

    try:
        cartoes_df = carregar_cartoes_credito()
        if cartoes_df.empty:
            st.info("ℹ️ Nenhum cartão cadastrado ainda.")
        else:
            cartoes_df = cartoes_df.rename(columns={"nome": "Cartão", "fechamento": "Fechamento (dia)"})
            st.markdown("### 📋 Cartões de Crédito Cadastrados")
            st.dataframe(cartoes_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar cartões: {e}")

# === Página: Cadastro de Saldos Bancários ===================================================
if st.session_state.get("mostrar_saldos_bancarios", False):
    st.markdown("## 🏦 Cadastro de Saldos Bancários por Data")

    data_saldo = st.date_input("Data do Saldo", value=date.today())
    data_saldo_str = str(data_saldo)

    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.execute("SELECT banco_1, banco_2, banco_3, banco_4 FROM saldos_bancos WHERE data = ?", (data_saldo_str,))
        resultado = cursor.fetchone()

    if resultado:
        st.info("🔄 Valores já cadastrados. Você pode atualizar.")
        banco_1 = st.number_input("Saldo Banco 1", value=resultado[0], step=10.0, format="%.2f")
        banco_2 = st.number_input("Saldo Banco 2", value=resultado[1], step=10.0, format="%.2f")
        banco_3 = st.number_input("Saldo Banco 3", value=resultado[2], step=10.0, format="%.2f")
        banco_4 = st.number_input("Saldo Banco 4", value=resultado[3], step=10.0, format="%.2f")
    else:
        st.warning("⚠️ Nenhum valor cadastrado para essa data.")
        banco_1 = st.number_input("Saldo Banco 1", step=10.0, format="%.2f")
        banco_2 = st.number_input("Saldo Banco 2", step=10.0, format="%.2f")
        banco_3 = st.number_input("Saldo Banco 3", step=10.0, format="%.2f")
        banco_4 = st.number_input("Saldo Banco 4", step=10.0, format="%.2f")

    if st.button("💾 Salvar Saldos"):
        try:
            with sqlite3.connect(caminho_banco) as conn:
                conn.execute("""
                    INSERT INTO saldos_bancos (data, banco_1, banco_2, banco_3, banco_4)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(data) DO UPDATE SET
                        banco_1=excluded.banco_1,
                        banco_2=excluded.banco_2,
                        banco_3=excluded.banco_3,
                        banco_4=excluded.banco_4
                """, (data_saldo_str, banco_1, banco_2, banco_3, banco_4))
                conn.commit()
            st.success("✅ Saldos salvos com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao salvar: {e}")
    
     # === Tabela de saldos anteriores ========================================================
    st.markdown("---")
    st.markdown("### 📋 Saldos Bancários Anteriores")

    try:
        with sqlite3.connect(caminho_banco) as conn:
            df_saldos = pd.read_sql("SELECT * FROM saldos_bancos ORDER BY data DESC LIMIT 15", conn)

        if not df_saldos.empty:
            df_saldos["data"] = pd.to_datetime(df_saldos["data"]).dt.strftime("%d/%m/%Y")

            for col in ["banco_1", "banco_2", "banco_3", "banco_4"]:
                df_saldos[col] = df_saldos[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

            st.dataframe(df_saldos, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum saldo registrado ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar saldos: {e}")


# === Página: Cadastro de Saldos de Caixa =========================================================================
if st.session_state.get("mostrar_cadastro_caixa", False) and perfil_usuario == "Administrador":
    st.markdown("## 💰 Cadastro de Caixa (Loja e Dinheiro Levado pra Casa)")

    data_caixa = st.date_input("Data de Referência", value=date.today())
    data_caixa_str = str(data_caixa)

    with sqlite3.connect(caminho_banco) as conn:
        cursor = conn.execute("SELECT caixa, caixa_2 FROM saldos_caixas WHERE data = ?", (data_caixa_str,))
        resultado = cursor.fetchone()

    if resultado:
        st.info("🔄 Valores já cadastrados. O valor digitado será **somado** ao valor já existente.")
        valor_novo_caixa = st.number_input("Adicionar ao Caixa (dinheiro na loja)", min_value=0.0, step=10.0, format="%.2f")
        valor_novo_caixa_2 = st.number_input("Adicionar ao Caixa 2 (dinheiro que levou pra casa)", min_value=0.0, step=10.0, format="%.2f")
        valor_final_caixa = resultado[0] + valor_novo_caixa
        valor_final_caixa_2 = resultado[1] + valor_novo_caixa_2
    else:
        st.warning("⚠️ Nenhum valor cadastrado para essa data. Informe o valor inicial.")
        valor_final_caixa = st.number_input("Caixa (dinheiro na loja)", min_value=0.0, step=10.0, format="%.2f")
        valor_final_caixa_2 = st.number_input("Caixa 2 (dinheiro que levou pra casa)", min_value=0.0, step=10.0, format="%.2f")

    if st.button("💾 Salvar Valores"):
        try:
            with sqlite3.connect(caminho_banco) as conn:
                if resultado:
                    # Atualiza somando ao valor anterior
                    conn.execute("""
                        UPDATE saldos_caixas
                        SET caixa = ?, caixa_2 = ?
                        WHERE data = ?
                    """, (valor_final_caixa, valor_final_caixa_2, data_caixa_str))
                else:
                    # Insere novo registro
                    conn.execute("""
                        INSERT INTO saldos_caixas (data, caixa, caixa_2)
                        VALUES (?, ?, ?)
                    """, (data_caixa_str, valor_final_caixa, valor_final_caixa_2))
                conn.commit()
            st.success("✅ Valores somados e salvos com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # Visualização dos últimos saldos
    st.markdown("---")
    st.markdown("### 📋 Últimos Registros")

    try:
        with sqlite3.connect(caminho_banco) as conn:
            df_caixa = pd.read_sql("SELECT * FROM saldos_caixas ORDER BY data DESC LIMIT 15", conn)

        if not df_caixa.empty:
            df_caixa["data"] = pd.to_datetime(df_caixa["data"]).dt.strftime("%d/%m/%Y")
            df_caixa["caixa"] = df_caixa["caixa"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            df_caixa["caixa_2"] = df_caixa["caixa_2"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.dataframe(df_caixa, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado cadastrado ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")

# === Página: Cadastro de Metas (com níveis ouro, prata e bronze) ===================================================
if perfil_usuario in ["Administrador", "Gerente"] and st.session_state.get("mostrar_cadastro_meta", False):
    st.markdown("## 🎯 Cadastro de Metas")

    # Carrega os usuários ativos
    try:
        with sqlite3.connect(caminho_banco) as conn:
            df_usuarios = pd.read_sql("SELECT id, nome FROM usuarios WHERE ativo = 1", conn)
        lista_usuarios = [("LOJA", 0)] + list(zip(df_usuarios["nome"], df_usuarios["id"]))
    except Exception as e:
        st.error(f"Erro ao carregar usuários: {e}")
        lista_usuarios = [("LOJA", 0)]

    nomes = [nome for nome, _ in lista_usuarios]
    vendedor_selecionado = st.selectbox("Selecione o Vendedor ou 'LOJA'", nomes)
    id_usuario = dict(lista_usuarios)[vendedor_selecionado]

    st.markdown("### 🗓️ Metas por Dia da Semana")
    col1, col2, col3 = st.columns(3)
    with col1:
        segunda = st.number_input("Segunda", min_value=0.0, step=10.0, format="%.2f")
        terca = st.number_input("Terça", min_value=0.0, step=10.0, format="%.2f")
        quarta = st.number_input("Quarta", min_value=0.0, step=10.0, format="%.2f")
    with col2:
        quinta = st.number_input("Quinta", min_value=0.0, step=10.0, format="%.2f")
        sexta = st.number_input("Sexta", min_value=0.0, step=10.0, format="%.2f")
        sabado = st.number_input("Sábado", min_value=0.0, step=10.0, format="%.2f")
    with col3:
        domingo = st.number_input("Domingo", min_value=0.0, step=10.0, format="%.2f")
        semanal = st.number_input("Meta Semanal", min_value=0.0, step=50.0, format="%.2f")
        mensal = st.number_input("Meta Mensal", min_value=0.0, step=100.0, format="%.2f")

    st.markdown("### 🥇 Metas por Nível")
    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        meta_ouro = st.number_input("Meta Ouro", min_value=0.0, step=100.0, format="%.2f")
    with col_n2:
        meta_prata = st.number_input("Meta Prata", min_value=0.0, step=100.0, format="%.2f")
    with col_n3:
        meta_bronze = st.number_input("Meta Bronze", min_value=0.0, step=100.0, format="%.2f")

    if st.button("💾 Salvar Metas"):
        try:
            with sqlite3.connect(caminho_banco) as conn:
                # Verifica se já existe meta para esse id_usuario
                cursor = conn.execute("SELECT id FROM metas WHERE id_usuario = ?", (id_usuario,))
                existe = cursor.fetchone()

                if existe:
                    conn.execute("""
                        UPDATE metas SET 
                            segunda = ?, terca = ?, quarta = ?, quinta = ?, sexta = ?, 
                            sabado = ?, domingo = ?, semanal = ?, mensal = ?,
                            meta_ouro = ?, meta_prata = ?, meta_bronze = ?,
                            vendedor = ?
                        WHERE id_usuario = ?
                    """, (
                        segunda, terca, quarta, quinta, sexta,
                        sabado, domingo, semanal, mensal,
                        meta_ouro, meta_prata, meta_bronze,
                        vendedor_selecionado.upper(),  # força padronização
                        id_usuario
                    ))
                else:
                    conn.execute("""
                        INSERT INTO metas (
                            id_usuario, vendedor, segunda, terca, quarta, quinta, sexta, sabado, domingo,
                            semanal, mensal, meta_ouro, meta_prata, meta_bronze
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        id_usuario, vendedor_selecionado.upper(), segunda, terca, quarta, quinta, sexta, sabado, domingo,
                        semanal, mensal, meta_ouro, meta_prata, meta_bronze
                    ))
                conn.commit()
            st.success("✅ Metas salvas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar metas: {e}")

    # === Visualização das Metas Cadastradas ===
    st.markdown("---")
    st.markdown("### 📋 Metas Cadastradas")

    try:
        with sqlite3.connect(caminho_banco) as conn:
            df_metas = pd.read_sql("""
                SELECT COALESCE(u.nome, m.vendedor, 'LOJA') AS Vendedor, 
                       m.segunda, m.terca, m.quarta, m.quinta, m.sexta, 
                       m.sabado, m.domingo, m.semanal, m.mensal,
                       m.meta_ouro, m.meta_prata, m.meta_bronze
                FROM metas m
                LEFT JOIN usuarios u ON m.id_usuario = u.id
                ORDER BY Vendedor
            """, conn)

        for col in df_metas.columns:
            if col != "Vendedor":
                df_metas[col] = df_metas[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(df_metas, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao carregar metas: {e}")