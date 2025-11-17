# PetDor/database/migration.py
"""
Sistema unificado de migração do PETDOR.
"""

import logging
from .connection import conectar_db

logger = logging.getLogger(__name__)


def criar_tabelas():
    """
    Cria todas as tabelas essenciais.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # -------------------------------
        # Usuários
        # -------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1
            );
        """)

        # -------------------------------
        # Pets
        # -------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutor_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                idade INTEGER,
                peso REAL,
                data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tutor_id) REFERENCES usuarios(id)
            );
        """)

        # -------------------------------
        # Avaliações
        # -------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                percentual_dor REAL NOT NULL,
                observacoes TEXT,
                data_avaliacao TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)

        # -------------------------------
        # Reset Senha
        # -------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)

        conn.commit()
        conn.close()
        logger.info("Migração executada com sucesso!")

    except Exception as e:
        logger.error(f"Erro na migração: {e}")
        raise


def migrar_banco_completo():
    """Função chamada pelo app.py"""
    criar_tabelas()

