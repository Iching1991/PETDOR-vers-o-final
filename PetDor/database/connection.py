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
# Caminho raiz do projeto
# -----------------------------------------
root_path = Path(__file__).resolve().parent.parent

# Garante que a raiz do projeto está no Python Path
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# --------------------------------------------------
# Importa config.py (que deve estar ao lado de app.py)
# --------------------------------------------------
try:
    from config import DATABASE_PATH as DB_PATH_RAW
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "❗ ERRO ao importar DATABASE_PATH do config.py.\n"
        "Certifique-se de que existe PetDor/config.py.\n",
    )

# Caminho absoluto do banco
DATABASE_PATH = str((root_path / DB_PATH_RAW).resolve())


def conectar_db():
    """Cria e retorna uma conexão SQLite."""
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
