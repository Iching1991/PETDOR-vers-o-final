# database/connection.py
from pathlib import Path
import sqlite3
import sys
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import DATABASE_PATH as DB_RAW

DATABASE_PATH = str((ROOT_DIR / DB_RAW).resolve())

def conectar_db():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
# PetDor/database/connection.py
"""
Gerenciamento de conexão SQLite do PETDOR
"""

import sqlite3
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Caminho absoluto do banco na raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = os.getenv("DATABASE_PATH", str(ROOT_DIR / "petdor.db"))

def conectar_db():
    """Conecta ao banco SQLite, criando diretório se necessário"""
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
