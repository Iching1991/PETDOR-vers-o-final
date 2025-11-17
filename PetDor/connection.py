"""
Gerenciamento de conexão com banco de dados SQLite do PETDOR
"""

import os
import sys
from pathlib import Path
import sqlite3
import logging

logger = logging.getLogger(__name__)

# -----------------------------------------
# 🔍 Localiza automaticamente o config.py
# -----------------------------------------
root_path = Path(__file__).resolve().parent.parent

# Garante que a raiz do projeto está no Python Path
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    from config import DATABASE_PATH
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "❗ ERRO: Não foi possível importar 'DATABASE_PATH' do config.py.\n"
        "Verifique se existe um arquivo config.py ao lado do app.py.\n"
        "Estrutura correta:\n\n"
        "PetDor/\n"
        "│ app.py\n"
        "│ config.py  <-- OBRIGATÓRIO\n"
        "└── database/\n"
    )

# -----------------------------------------
# 🔌 Função de conexão
# -----------------------------------------
def conectar_db():
    """
    Conecta ao banco de dados SQLite.
    Returns:
        sqlite3.Connection
    """
    try:
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        raise


# -----------------------------------------
# 🏗 Inicialização e criação das tabelas
# -----------------------------------------
def init_database():
    """Cria todas as tabelas básicas se não existirem."""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1
            )
        """)

        # Pets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutor_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                idade INTEGER,
                peso REAL,
                data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tutor_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Avaliações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                percentual_dor REAL NOT NULL,
                observacoes TEXT,
                data_avaliacao TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Reset de senha
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

        logger.info("Banco de dados inicializado com sucesso!")
        return True

    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")
        return False


if __name__ == "__main__":
    # Execução manual no terminal
    if init_database():
        print("Banco de dados PETDOR inicializado com sucesso!")
    else:
        print("Erro ao inicializar banco de dados.")
