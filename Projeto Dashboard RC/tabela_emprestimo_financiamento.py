import sqlite3
import os

# Caminho correto para o seu banco
caminho_banco = os.path.join(
    "C:\\Users\\User\\OneDrive\\Documentos\\Python\\Dev_Python\\Abud Python Workspace - GitHub\\Projeto Dashboard RC\\data",
    "dashboard_rc.db"
)

# Conectar e criar a tabela
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS emprestimos_financiamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_contratacao TEXT NOT NULL,
    valor_total REAL NOT NULL,
    tipo TEXT NOT NULL,
    banco TEXT,
    parcelas_total INTEGER NOT NULL,
    parcelas_pagas INTEGER DEFAULT 0,
    valor_parcela REAL,
    taxa_juros_am REAL,
    vencimento_dia INTEGER,
    status TEXT DEFAULT 'Em aberto',
    usuario TEXT,
    data_quitacao TEXT,
    origem_recursos TEXT,
    valor_pago REAL DEFAULT 0.0,
    valor_em_aberto REAL,
    renegociado_de INTEGER,
    descricao TEXT
);
""")

conn.commit()
conn.close()

print("✅ Tabela 'emprestimos_financiamentos' criada com sucesso!")