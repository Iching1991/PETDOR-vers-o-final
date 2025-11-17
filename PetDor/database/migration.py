"""
Migrações do banco de dados PETDOR
"""

import sys
import sqlite3
import logging
from pathlib import Path

# -----------------------------------------
# Ajuste do path do projeto
# -----------------------------------------
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from config import DATABASE_PATH
from .connection import conectar_db  # ✅ Conexão centralizada

logger = logging.getLogger(__name__)


# -----------------------------------------
# Funções auxiliares
# -----------------------------------------
def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [info[1] for info in cursor.fetchall()]
    return coluna in colunas


def adicionar_coluna(cursor, tabela, coluna, tipo):
    if not coluna_existe(cursor, tabela, coluna):
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
        print(f"✔ Coluna adicionada em {tabela}: {coluna}")
    else:
        print(f"ℹ Coluna já existe: {tabela}.{coluna}")


# -----------------------------------------
# MIGRAÇÃO: Tabela usuários
# -----------------------------------------
def criar_tabela_usuarios():
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                is_admin INTEGER DEFAULT 0,
                tipo_usuario TEXT DEFAULT 'tutor',
                cnpj TEXT,
                endereco TEXT,
                crmv TEXT,
                especialidade TEXT,
                data_desativacao TEXT,
                motivo_desativacao TEXT,
                email_confirmado INTEGER DEFAULT 0,
                token_confirmacao TEXT
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Tabela 'usuarios' OK")
        return True

    except Exception as e:
        print(f"❌ Erro ao criar tabela usuarios: {e}")
        return False


# -----------------------------------------
# MIGRAÇÃO: Tabela pets
# -----------------------------------------
def criar_tabela_pets():
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutor_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                data_nascimento TEXT,
                sexo TEXT,
                peso REAL,
                observacoes TEXT,
                data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tutor_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Tabela 'pets' OK")
        return True

    except Exception as e:
        print(f"❌ Erro ao criar tabela pets: {e}")
        return False


# -----------------------------------------
# MIGRAÇÃO: Tabela avaliações
# -----------------------------------------
def criar_tabela_avaliacoes():
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                data_avaliacao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                percentual_dor REAL NOT NULL,
                observacoes TEXT,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Tabela 'avaliacoes' OK")
        return True

    except Exception as e:
        print(f"❌ Erro ao criar tabela avaliacoes: {e}")
        return False


# -----------------------------------------
# MIGRAÇÃO: Tabela respostas
# -----------------------------------------
def criar_tabela_avaliacao_respostas():
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacao_respostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                avaliacao_id INTEGER NOT NULL,
                pergunta_id TEXT NOT NULL,
                resposta TEXT NOT NULL,
                FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Tabela 'avaliacao_respostas' OK")
        return True

    except Exception as e:
        print(f"❌ Erro ao criar tabela avaliacao_respostas: {e}")
        return False


# -----------------------------------------
# 🚀 Executor geral
# -----------------------------------------
def migrar_banco_completo():
    print("\n🔄 Executando migrações completas do PETDOR...\n")

    migracoes = [
        ("Tabela de usuários", criar_tabela_usuarios),
        ("Tabela de pets", criar_tabela_pets),
        ("Tabela de avaliações", criar_tabela_avaliacoes),
        ("Tabela de respostas", criar_tabela_avaliacao_respostas),
    ]

    for nome, func in migracoes:
        print(f"\n📢 Migrando: {nome}")
        func()

    print("\n🎉 Migrações concluídas!\n")


if __name__ == "__main__":
    migrar_banco_completo()
