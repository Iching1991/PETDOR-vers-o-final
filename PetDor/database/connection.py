import sqlite3
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

def conectar_db():
    try:
        # Garante diretório
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        raise
