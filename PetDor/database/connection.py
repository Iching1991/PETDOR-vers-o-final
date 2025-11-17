import sqlite3
import os

DB_PATH = "petdor.db"

def conectar_db():
    """Retorna uma conexão SQLite garantida."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) if "/" in DB_PATH else None
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
