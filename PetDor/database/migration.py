"""
Sistema de MIGRAÇÕES oficial do PETDOR.

Funções:
- Registrar migrações executadas
- Criar tabelas
- Rodar apenas migrações novas
"""

import sqlite3
from pathlib import Path
import sys

# Adiciona raiz ao path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from connection import DATABASE_PATH, conectar_db


# -----------------------------------------
# 🔍 Controle de migrações
# -----------------------------------------
def migra_executada(nome):
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM migrations WHERE nome = ?", (nome,))
    done = cur.fetchone()

    conn.close()
    return done is not None


def registrar_migracao(nome):
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO migrations (nome) VALUES (?)", (nome,))
    conn.commit()
    conn.close()


# -----------------------------------------
# 🏗 Migrações oficiais PETDOR
# -----------------------------------------
def m001_usuarios():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            ativo INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


def m002_pets():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tutor_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            peso REAL,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tutor_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def m003_avaliacoes():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
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

    conn.commit()
    conn.close()


def m004_password_reset():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
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


# -----------------------------------------
# 🚀 Executor geral de migrações
# -----------------------------------------
MIGRACOES = [
    ("m001_usuarios", m001_usuarios),
    ("m002_pets", m002_pets),
    ("m003_avaliacoes", m003_avaliacoes),
    ("m004_password_reset", m004_password_reset),
]


def migrar_banco_completo():
    print("\n🔄 Executando migrações do PETDOR...\n")

    for nome, func in MIGRACOES:
        if not migra_executada(nome):
            print(f"▶ Rodando: {nome}")
            func()
            registrar_migracao(nome)
            print(f"✔ Finalizado: {nome}")
        else:
            print(f"⏭ Já executado: {nome}")

    print("\n🎉 Banco atualizado com sucesso!\n")


if __name__ == "__main__":
    migrar_banco_completo()
