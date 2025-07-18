import sqlite3
import os

# === Caminho da pasta e banco de dados ===
caminho_data = r'C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data'
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# === Conectar (ou criar) o banco de dados SQLite ===
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

# === Criar tabela de entradas ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS entrada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Data TEXT,
    Valor REAL,
    Forma_de_Pagamento TEXT,
    Parcelas INTEGER,
    Bandeira TEXT
)
''')

# === Criar tabela de saídas ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS saida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Data TEXT,
    Valor REAL,
    Forma_de_Pagamento TEXT,
    Parcelas INTEGER,
    Categoria TEXT,
    Sub_Categoria TEXT,
    Descricao TEXT
)
''')

# === Criar tabela de mercadorias ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS mercadorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Data TEXT,
    Colecao TEXT,
    Fornecedor TEXT,
    Valor_Mercadoria REAL,
    Frete REAL,
    Forma_Pagamento TEXT,
    Parcelas INTEGER,
    Previsao_Faturamento TEXT,
    Faturamento REAL,
    Previsao_Recebimento TEXT,
    Recebimento REAL,
    Numero_Pedido TEXT,
    Numero_NF TEXT
)
''')

# === Criar tabela de taxas das máquinas de cartão ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS taxas_maquinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forma_pagamento TEXT NOT NULL,  -- 'débito' ou 'crédito'
    bandeira TEXT NOT NULL,
    parcelas INTEGER,               -- NULL para débito, 1 a 12 para crédito
    taxa_percentual REAL NOT NULL
)
""")

# === Criar tabela de contas a pagar ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS contas_a_pagar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_compra DATE NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    tipo_pagamento TEXT NOT NULL,
    parcelas INTEGER,
    vencimento DATE NOT NULL,
    categoria TEXT,
    subcategoria TEXT,
    numero_pedido TEXT,
    numero_nf TEXT,
    pago BOOLEAN DEFAULT 0,
    data_pagamento DATE
)
""")

# === Criar tabela de usuários do sistema ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT,
    senha TEXT,
    perfil TEXT DEFAULT 'admin', -- 'admin', 'funcionario', etc.
    ativo BOOLEAN DEFAULT 1
)
""")

# === Finalizar e fechar conexão ===
conn.commit()
conn.close()

print("✅ Banco de dados verificado com sucesso! Todas as tabelas estão criadas e nenhum dado foi apagado.")