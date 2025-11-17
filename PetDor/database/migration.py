"""
Migrações do banco de dados PETDOR
"""

import sqlite3
import logging
from .connection import conectar
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# 🔧 Funções auxiliares
# ---------------------------------------------------------
def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [info[1] for info in cursor.fetchall()]
    return coluna in colunas


def adicionar_coluna(cursor, tabela, coluna, tipo):
    if not coluna_existe(cursor, tabela, coluna):
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
        print(f"✔ Coluna adicionada à tabela {tabela}: {coluna}")
    else:
        print(f"ℹ Coluna já existe na tabela {tabela}: {coluna}")


# ---------------------------------------------------------
# 🐾 MIGRAÇÕES PRINCIPAIS
# ---------------------------------------------------------
def criar_tabela_usuarios():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                data_registro TEXT NOT NULL,
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


def criar_tabela_pets():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
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


def criar_tabela_avaliacoes():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                data_avaliacao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                percentual_dor INTEGER NOT NULL,
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


def criar_tabela_avaliacao_respostas():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
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


# ---------------------------------------------------------
# 🛠 Ajustes posteriores
# ---------------------------------------------------------
def migracoes_extra():
    """Adiciona colunas que podem ter faltado historicamente"""
    try:
        conn = conectar()
        cursor = conn.cursor()

        print("\n🔍 Verificando colunas extras da tabela 'pets'...")

        extras_pets = {
            "raca": "TEXT",
            "data_nascimento": "TEXT",
            "sexo": "TEXT",
            "peso": "REAL"
        }

        for coluna, tipo in extras_pets.items():
            adicionar_coluna(cursor, "pets", coluna, tipo)

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print("❌ Erro nas migrações extras:", e)
        return False


# ---------------------------------------------------------
# 🚀 EXECUTAR TODAS AS MIGRAÇÕES
# ---------------------------------------------------------
def migrar_banco_completo():
    print("\n🔄 Executando migrações completas do PETDOR...\n")

    migracoes = [
        criar_tabela_usuarios,
        criar_tabela_pets,
        criar_tabela_avaliacoes,
        criar_tabela_avaliacao_respostas,
        migracoes_extra
    ]

    sucesso = 0
    falhas = 0

    for funcao in migracoes:
        nome = funcao.__name__
        print(f"\n📋 Executando: {nome}...")
        if funcao():
            sucesso += 1
        else:
            falhas += 1

    print("\n==============================================")
    print(f"✅ Migrações bem-sucedidas: {sucesso}")
    print(f"❌ Falhas: {falhas}")
    print("==============================================\n")

    return falhas == 0


if __name__ == "__main__":
    migrar_banco_completo()

