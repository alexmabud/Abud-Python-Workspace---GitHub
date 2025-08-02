
# === MÓDULO UTILS ==========================================================================================
import pandas as pd
import hashlib
from datetime import timedelta
from workalendar.america import BrazilDistritoFederal

def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_percentual(valor, meta):
    try:
        return round((valor / meta) * 100, 2) if meta else 0
    except ZeroDivisionError:
        return 0

def adicionar_dia_semana(df):
    df['Dia da Semana'] = pd.to_datetime(df['Data']).dt.day_name(locale='pt_BR')
    return df

def ultimo_dia_util(data):
    cal = BrazilDistritoFederal()
    data = pd.to_datetime(data)
    while not cal.is_working_day(data.date()):
        data -= timedelta(days=1)
    return data

def senha_forte(senha):
    import re
    if (len(senha) >= 8 and
        re.search(r"[A-Z]", senha) and
        re.search(r"[a-z]", senha) and
        re.search(r"[0-9]", senha) and
        re.search(r"[!@#$%^&*(),.?":{}|<>]", senha)):
        return True
    return False

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# === MÓDULO DASHBOARD ======================================================================================
import streamlit as st
import plotly.graph_objects as go

def bloco_comissoes(df, metas, hoje, perfil):
    pass  # lógica a implementar

def bloco_destaque(df_entrada):
    pass

def bloco_destaque_2(df_saida):
    pass

def bloco_destaque_3(df_mercadorias):
    pass

def bloco_destaque_4(df_entrada, df_saida, df_mercadorias):
    pass

def bloco_saldo_total(fechamentos, data):
    pass

def gerar_gauge(valor, titulo, nivel, cor):
    pass

def grafico_meta_percentual(valor, meta, titulo):
    pass

def graficos_vendedores(df, hoje, inicio_semana, inicio_mes):
    pass

def extrair_metas(metas, coluna_dia):
    pass


# === MÓDULO BANCO ==========================================================================================
import sqlite3

def carregar_cartoes_credito():
    pass

def carregar_metas():
    pass

def carregar_tabela(nome_tabela):
    pass


# === MÓDULO AUTH ===========================================================================================
def exibir_usuario_logado(email, perfil):
    pass

def limpar_todas_as_paginas():
    pass

def verificar_acesso(pagina):
    pass


# === MÓDULO LANCAMENTOS ====================================================================================
def calcular_valor_liquido_cartao(row, df_taxas):
    pass

def saida_por_banco(df_saida, data_lancamento):
    pass
