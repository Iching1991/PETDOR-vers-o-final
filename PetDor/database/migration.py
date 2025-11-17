"""
Migrações do banco de dados PETDOR
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import sqlite3
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

def criar_tabela_usuarios():
    """Cria a tabela de usuários."""
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
        logger.info("Tabela 'usuarios' criada/verificada")
        print("✅ Tabela 'usuarios' OK")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela usuarios: {e}")
        print(f"❌ Erro ao criar tabela usuarios: {e}")
        return False

def criar_tabela_pets():
    """Cria a tabela de pets."""
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
        logger.info("Tabela 'pets' criada/verificada")
        print("✅ Tabela 'pets' OK")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela pets: {e}")
        print(f"❌ Erro ao criar tabela pets: {e}")
        return False

def criar_tabela_avaliacoes():
    """Cria a tabela de avaliações de dor."""
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
        logger.info("Tabela 'avaliacoes' criada/verificada")
        print("✅ Tabela 'avaliacoes' OK")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela avaliacoes: {e}")
        print(f"❌ Erro ao criar tabela avaliacoes: {e}")
        return False

def adicionar_colunas_desativacao():
    """Adiciona colunas para soft delete de usuários"""
    # ... (código fornecido) ...

def adicionar_campo_admin():
    """Adiciona campo is_admin para controle de administradores"""
    # ... (código fornecido) ...

def adicionar_campo_tipo_usuario():
    """Adiciona campos para tipo de usuário (tutor, clinica, veterinario)"""
    # ... (código fornecido) ...

def adicionar_campos_confirmacao_email():
    """Adiciona campos para confirmação de email."""
    # ... (código fornecido) ...

def criar_tabela_compartilhamentos():
    """Cria tabela para compartilhamento de pets com profissionais."""
    # ... (código fornecido) ...

def criar_tabela_notificacoes():
    """Cria tabela para notificações de dor e eventos"""
    # ... (código fornecido) ...

def criar_tabela_avaliacao_respostas():
    """Cria a tabela para armazenar as respostas das perguntas de avaliação."""
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
        logger.info("Tabela 'avaliacao_respostas' criada/verificada")
        print("✅ Tabela 'avaliacao_respostas' OK")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela avaliacao_respostas: {e}")
        print(f"❌ Erro ao criar tabela avaliacao_respostas: {e}")
        return False

def migrar_banco_completo():
    """Executa todas as migrações do banco de dados"""
    print("\n🔄 Executando migrações completas do PETDor...\n")

    migracoes = [
        ("Tabela de usuários", criar_tabela_usuarios),
        ("Tabela de pets", criar_tabela_pets),
        ("Tabela de avaliações", criar_tabela_avaliacoes),
        ("Colunas de desativação", adicionar_colunas_desativacao),
        ("Campo is_admin", adicionar_campo_admin),
        ("Campos de tipo de usuário", adicionar_campo_tipo_usuario),
        ("Campos de confirmação de email", adicionar_campos_confirmacao_email),
        ("Tabela de compartilhamentos", criar_tabela_compartilhamentos),
        ("Tabela de notificações", criar_tabela_notificacoes),
        ("Tabela de respostas de avaliação", criar_tabela_avaliacao_respostas),
    ]

    sucessos = 0
    falhas = 0

    for nome, funcao in migracoes:
        print(f"\n📋 Migrando: {nome}...")
        if funcao():
            sucessos += 1
        else:
            falhas += 1
            print(f"⚠️ Falha em: {nome}")

    print(f"\n{'='*60}")
    print(f"✅ Migrações concluídas: {sucessos} sucessos")
    if falhas > 0:
        print(f"❌ Falhas: {falhas}")
    else:
        print("🎉 Todas as migrações executadas com sucesso!")
    print(f"{'='*60}\n")

    return falhas == 0

if __name__ == "__main__":
    migrar_banco_completo()
