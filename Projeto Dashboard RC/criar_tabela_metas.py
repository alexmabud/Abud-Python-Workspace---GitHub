import sqlite3
import os

# Caminho da pasta onde está o banco de dados
caminho_data = os.path.join(os.path.dirname(__file__), 'data')
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Cria a nova tabela de metas com coluna 'vendedor'
def criar_tabela_metas():
    with sqlite3.connect(caminho_banco) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,             -- 'diária', 'semanal', 'mensal'
                nivel TEXT,            -- 'ouro', 'prata', 'bronze'
                valor REAL,
                data_referencia DATE,  -- para diária: o dia; para semanal: segunda-feira da semana; para mensal: dia 01 do mês
                vendedor TEXT DEFAULT 'LOJA'  -- Pode ser nome do vendedor ou 'LOJA' para metas gerais
            );
        """)
        conn.commit()
        print("✅ Tabela 'metas' criada com sucesso!")

if __name__ == "__main__":
    criar_tabela_metas()