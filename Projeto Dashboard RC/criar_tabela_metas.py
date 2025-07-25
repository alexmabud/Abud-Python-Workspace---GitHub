import sqlite3
import os

# Caminho da pasta onde está o banco de dados
caminho_data = os.path.join(os.path.dirname(__file__), 'data')
caminho_banco = os.path.join(caminho_data, 'dashboard_rc.db')

# Cria a nova tabela de metas por usuário com dias da semana + semanal e mensal
def criar_tabela_metas():
    with sqlite3.connect(caminho_banco) as conn:
        conn.execute("DROP TABLE IF EXISTS metas")  # Apaga a tabela antiga, se existir
        conn.execute("""
            CREATE TABLE metas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                segunda REAL DEFAULT 0.0,
                terca REAL DEFAULT 0.0,
                quarta REAL DEFAULT 0.0,
                quinta REAL DEFAULT 0.0,
                sexta REAL DEFAULT 0.0,
                sabado REAL DEFAULT 0.0,
                domingo REAL DEFAULT 0.0,
                semanal REAL DEFAULT 0.0,
                mensal REAL DEFAULT 0.0,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            );
        """)
        conn.commit()
        print("✅ Tabela 'metas' criada com sucesso!")

if __name__ == "__main__":
    criar_tabela_metas()