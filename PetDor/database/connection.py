# PetDor/database/connection.py
"""
Gerenciamento central de conexão com SQLite do PETDOR
"""

import os
import sqlite3
import logging
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

# ---------------------------------------
# 🔍 Localiza o config.py automaticamente
# ---------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent  # pasta PetDor/

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from config import DATABASE_PATH as DB_RAW
except Exception:
    raise ModuleNotFoundError(
        "❌ config.py não encontrado ou DATABASE_PATH ausente."
    )

# Caminho absoluto unificado do banco
DATABASE_PATH = str((ROOT_DIR / DB_RAW).resolve())


def conectar_db():
    """
    Abre conexão com SQLite e garante criação do diretório.
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
