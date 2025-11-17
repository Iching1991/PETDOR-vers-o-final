"""
Módulo de migração do banco PETDOR.
Unifica criação de tabelas e atualizações.
"""

import logging
from .connection import conectar_db

logger = logging.getLogger(__name__)


def migrar_banco_completo():
    """Cria ou atualiza todas as tabelas do sistema PETDOR."""
    try:
        conn = conectar_db()
        c = conn.cursor()

        # -----------------------------
        # Tabela usuários
        # -----------------------------
        c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1
            )
        """)

        # -----------------------------
        # Pets
        # -----------------------------
        c.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutor_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                idade INTEGER,
                peso REAL,
                data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tutor_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # -----------------------------
        # Avaliações de dor
        # -----------------------------
        c.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                percentual_dor REAL NOT NULL,
                observacoes TEXT,
                data_avaliacao TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # -----------------------------
        # Recuperação de senha
        # -----------------------------
        c.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

        logger.info("Migração concluída com sucesso!")
        return True

    except Exception as e:
        logger.error(f"Erro na migração do banco: {e}")
        raise
