# PetDor/database/connection.py
"""
Conexão central do banco SQLite do PETDOR
"""

import sqlite3
import os
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)

# -------------------------------
# 🔍 Localiza o config.py na raiz
# -------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent  # PetDor/
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from config import DATABASE_PATH
except ModuleNotFoundError:
    DATABASE_PATH = str(ROOT_DIR / "petdor.db")
    logger.warning("Não foi possível importar DATABASE_PATH do config.py. Usando padrão petdor.db na raiz.")

# -------------------------------
# 🔌 Função de conexão
# -------------------------------
def conectar_db():
    """
    Conecta ao banco SQLite, criando diretório se necessário
    """
    try:
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    except Exception as e:
        logger.error(f"[ERRO] Falha ao conectar ao banco: {e}")
        raise
