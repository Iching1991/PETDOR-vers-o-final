"""
Criação e migração de tabelas do PETDOR
"""

import logging
from .connection import conectar_db

logger = logging.getLogger(__name__)


def criar_tabelas():
    """Cria todas as tabelas necessárias do sistema PETDOR."""
    conn = conectar_db()
    cursor = conn.cursor()

    # ----------------------------------------
    # 🔧 Ativa suporte a FOREIGN KEY no SQLite
    # ----------------------------------------
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ----------------------------------------
    # 👤 Tabela: Usuários
    # ----------------------------------------
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

    # ----------------------------------------
    # 🐾 Tabela: Pets
    # ----------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutor_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            peso REAL,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tutor_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    """)

    # ----------------------------------------
    # 📋 Tabela: Avaliações de dor
    # ----------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            percentual_dor REAL NOT NULL,
            observacoes TEXT,
            data_avaliacao TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    """)

    # ----------------------------------------
    # 🔑 Reset de senha
    # ----------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

    logger.info("✔ Todas as tabelas foram criadas/migradas com sucesso.")


def migrar_banco_completo():
    """
    Executa todas as migrações necessárias no banco.
    Pode crescer com novas versões.
    """
    logger.info("🔄 Iniciando migração completa do banco...")
    criar_tabelas()
    logger.info("🏁 Migração finalizada.")
