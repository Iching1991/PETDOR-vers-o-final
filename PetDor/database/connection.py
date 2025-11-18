"""
Conexão central do banco SQLite do PETDOR
"""

import sqlite3
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# -----------------------------------------------
# 📌 Diretório raiz do projeto (PetDor/)
# -----------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------
# 📌 Caminho padrão do banco
#     Se DATABASE_PATH NÃO for informado via .env,
#     o banco ficará em: PetDor/petdor.db
# -----------------------------------------------
DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    str(ROOT_DIR / "petdor.db")
)

def conectar_db():
    """
    Conecta ao banco SQLite.
    Cria diretórios automaticamente se necessário.
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
