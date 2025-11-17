"""
Gerenciamento da conexão com o banco SQLite do PETDOR.
Centraliza:
- Caminho do banco
- Conexão segura
- Inicialização mínima
"""

import os
import sys
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# -----------------------------------------
# 📌 Localização automática do config.py
# -----------------------------------------
root_path = Path(__file__).resolve().parent

project_root = root_path.parent  # pasta PetDor/

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from config import DATABASE_PATH as DB_PATH_RAW
except Exception:
    raise ModuleNotFoundError(
        "\n❗ ERRO: config.py não encontrado!\n"
        "Estrutura correta:\n"
        "PetDor/\n"
        "│ app.py\n"
        "│ config.py   ← obrigatório\n"
        "└── database/\n"
    )

# Caminho absoluto
DATABASE_PATH = str((project_root / DB_PATH_RAW).resolve())


# -----------------------------------------
# 🔌 Conexão com o banco
# -----------------------------------------
def conectar_db():
    """Retorna uma conexão SQLite já configurada."""
    try:
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    except Exception as e:
        logger.error(f"Erro ao conectar no banco: {e}")
        raise


# -----------------------------------------
# 🏗 Inicialização mínima (somente segurança)
# -----------------------------------------
def init_database():
    """
    Cria estrutura básica obrigatória:
    - Apenas tabela de controle se necessário
    Migrações FARÃO o resto.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # tabela "migrations" controla quais migrações já rodaram
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                data_execucao TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

        logger.info("Banco inicializado (estrutura mínima).")
        return True

    except Exception as e:
        logger.error(f"Erro no init_database(): {e}")
        return False
