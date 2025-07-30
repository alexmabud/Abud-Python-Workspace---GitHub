import sqlite3

# CAMINHO do seu banco de dados
caminho_banco = r'C:\Users\User\OneDrive\Documentos\Python\Dev_Python\Abud Python Workspace - GitHub\Projeto Dashboard RC\data\dashboard_rc.db'

# Lista de comandos para adicionar as colunas
alteracoes = [
    ("caixa_vendas", "REAL", 0.0),
    ("caixa_total", "REAL", 0.0),
    ("caixa2_dia", "REAL", 0.0),
    ("caixa2_total", "REAL", 0.0),
]

with sqlite3.connect(caminho_banco) as conn:
    cursor = conn.cursor()
    # Busca colunas existentes
    colunas = [col[1] for col in cursor.execute("PRAGMA table_info(saldos_caixas)").fetchall()]
    for nome, tipo, valor in alteracoes:
        if nome not in colunas:
            sql = f"ALTER TABLE saldos_caixas ADD COLUMN {nome} {tipo} DEFAULT {valor};"
            print(f"Adicionando coluna: {nome}")
            cursor.execute(sql)
        else:
            print(f"Coluna já existe: {nome}")
    conn.commit()

print("Tabela alterada com sucesso!")