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
# Importa config.py
# -----------------------------------------
try:
    from config import DATABASE_PATH
except Exception:
    raise ModuleNotFoundError(
        "❗ ERRO: Não foi possível importar DATABASE_PATH do config.py.\n"
        "Verifique se config.py está na mesma pasta do app.py."
    )


def conectar_db():
    """Conecta ao banco de dados usando o caminho absoluto definido no config.py."""
    try:
        # Garante que o diretório existe
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        raise
