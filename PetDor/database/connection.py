"""
Gerenciamento de conexão com banco de dados
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Agora importe os módulos locais
import sqlite3
from contextlib import contextmanager
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    """Context manager para conexão segura"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro no banco: {e}")
        raise
    finally:
        conn.close()

def init_database():
    """Inicializa as tabelas"""
    with get_db() as conn:
        cur = conn.cursor()

        # Tabela de usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash BLOB NOT NULL,
                data_criacao TEXT NOT NULL,
                ativo INTEGER DEFAULT 1
            )
        """)

        # Tabela de avaliações
        cur.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                pet_nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                respostas TEXT NOT NULL,
                pontuacao_total INTEGER NOT NULL,
                pontuacao_maxima INTEGER NOT NULL,
                percentual REAL NOT NULL,
                data_avaliacao TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Tabela de reset de senha
        cur.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        logger.info("Banco de dados inicializado")
