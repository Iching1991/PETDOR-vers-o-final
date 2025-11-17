"""
Migrações do banco de dados PETDor
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


def adicionar_colunas_desativacao():
    """Adiciona colunas para soft delete de usuários"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'data_desativacao' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN data_desativacao TEXT")
            print("✅ Campo 'data_desativacao' adicionado")
        if 'motivo_desativacao' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN motivo_desativacao TEXT")
            print("✅ Campo 'motivo_desativacao' adicionado")
        conn.commit()
        conn.close()
        logger.info("Colunas de desativação adicionadas")
        return True
    except Exception as e:
        logger.error(f"Erro ao adicionar colunas de desativação: {e}")
        print(f"❌ Erro: {e}")
        return False


def adicionar_campo_admin():
    """Adiciona campo is_admin para controle de administradores"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'is_admin' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0")
            print("✅ Campo 'is_admin' adicionado")
        conn.commit()
        conn.close()
        logger.info("Campo is_admin adicionado")
        return True
    except Exception as e:
        logger.error(f"Erro ao adicionar campo is_admin: {e}")
        print(f"❌ Erro: {e}")
        return False


def adicionar_campo_tipo_usuario():
    """Adiciona campos para tipo de usuário (tutor, clinica, veterinario)"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'tipo_usuario' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo_usuario TEXT DEFAULT 'tutor'")
            print("✅ Campo 'tipo_usuario' adicionado")
        if 'cnpj' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN cnpj TEXT")
            print("✅ Campo 'cnpj' adicionado")
        if 'endereco' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN endereco TEXT")
            print("✅ Campo 'endereco' adicionado")
        if 'crmv' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN crmv TEXT")
            print("✅ Campo 'crmv' adicionado")
        if 'especialidade' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN especialidade TEXT")
            print("✅ Campo 'especialidade' adicionado")

        conn.commit()
        conn.close()
        logger.info("Campos de tipo de usuário adicionados")
        return True
    except Exception as e:
        logger.error(f"Erro ao adicionar campos de tipo de usuário: {e}")
        print(f"❌ Erro: {e}")
        return False


def adicionar_campos_confirmacao_email():
    """Adiciona campos para confirmação de email e token"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'email_confirmado' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN email_confirmado INTEGER DEFAULT 0")
            print("✅ Campo 'email_confirmado' adicionado")
        if 'token_confirmacao' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN token_confirmacao TEXT")
            print("✅ Campo 'token_confirmacao' adicionado")
        if 'data_expiracao_token' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN data_expiracao_token TEXT")
            print("✅ Campo 'data_expiracao_token' adicionado")

        conn.commit()
        conn.close()
        logger.info("Campos de confirmação de email adicionados")
        return True
    except Exception as e:
        logger.error(f"Erro ao adicionar campos de confirmação: {e}")
        print(f"❌ Erro: {e}")
        return False


def criar_tabela_compartilhamentos():
    """Cria tabela para compartilhamento de pets entre tutor e profissionais"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compartilhamentos_pet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                tutor_id INTEGER NOT NULL,
                profissional_id INTEGER NOT NULL,
                data_compartilhamento TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                token_acesso TEXT UNIQUE,
                data_expiracao TEXT,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (tutor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (profissional_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Cria índices para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_compartilhamentos_pet 
            ON compartilhamentos_pet(pet_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_compartilhamentos_tutor 
            ON compartilhamentos_pet(tutor_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_compartilhamentos_profissional 
            ON compartilhamentos_pet(profissional_id)
        """)

        conn.commit()
        conn.close()
        logger.info("Tabela 'compartilhamentos_pet' criada/verificada")
        print("✅ Tabela 'compartilhamentos_pet' OK")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela compartilhamentos: {e}")
        print(f"❌ Erro: {e}")
        return False


def criar_tabela_notificacoes():
    """Cria tabela para notificações de dor e eventos"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                pet_id INTEGER NOT NULL,
                avaliacao_id INTEGER,
                tipo TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                nivel_prioridade INTEGER DEFAULT 2,
                lida INTEGER DEFAULT 0,
                data_criacao TEXT NOT NULL,
                data_leitura TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes(id) ON DELETE CASCADE
            )
        """)

        # Cria índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notificacoes_usuario 
            ON notificacoes(usuario_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notificacoes_nao_lidas 
            ON notificacoes(usuario_id, lida) WHERE lida = 0
        """)

        conn.commit()
        conn.close()
        logger.info("Tabela 'notificacoes' criada/verificada")
        print("✅ Tabela 'notificacoes' OK")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela notificacoes: {e}")
        print(f"❌ Erro: {e}")
        return False


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
        print(f"❌ Erro: {e}")
        return False


def migrar_banco_completo():
    """Executa todas as migrações do banco de dados"""
    print("\n🔄 Executando migrações completas do PETDor...\n")

    migracoes = [
        ("Colunas de desativação", adicionar_colunas_desativacao),
        ("Campo is_admin", adicionar_campo_admin),
        ("Campos de tipo de usuário", adicionar_campo_tipo_usuario),
        ("Campos de confirmação de email", adicionar_campos_confirmacao_email),
        ("Tabela de compartilhamentos", criar_tabela_compartilhamentos),
        ("Tabela de notificações", criar_tabela_notificacoes),
        ("Tabela de respostas de avaliação", criar_tabela_avaliacao_respostas), # Esta linha já estava correta!
    ]

    sucessos = 0
    falhas = 0

    for nome, funcao in migracoes:
        print(f"\n📋 Migrando: {nome}...")
        if funcao():
            sucessos += 1
        else:
            falhas += 1
            print(f"⚠️ Fal:
        print(f"❌ Falhas: {falhas}")
    else:
        print("🎉 Todas as migrações executadas com sucesso!")
    print(f"{'='*60}\n")

    return falhas == 0


if __name__ == "__main__":
    migrar_banco_completo()

