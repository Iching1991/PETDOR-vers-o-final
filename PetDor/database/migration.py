"""
Migrações do banco de dados PETDor
"""
import sqlite3
import logging
from datetime import datetime
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def conectar_db():
    """Conecta ao banco de dados"""
    return sqlite3.connect(DATABASE_PATH)


def adicionar_campo_tipo_usuario():
    """Adiciona campo tipo_usuario na tabela usuarios"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'tipo_usuario' not in colunas:
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN tipo_usuario TEXT DEFAULT 'tutor'
            """)
            logger.info("Coluna 'tipo_usuario' adicionada")
            print("✅ Campo 'tipo_usuario' adicionado (default = tutor)")
        else:
            print("✅ Campo 'tipo_usuario' já existe")

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Erro ao adicionar tipo_usuario: {e}")
        return False


def criar_tabela_vinculos_pets():
    """Cria tabela para vincular pets a múltiplos profissionais"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se tabela já existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vinculos_pets'")
        if cursor.fetchone():
            print("✅ Tabela 'vinculos_pets' já existe")
            conn.close()
            return True

        # Cria tabela de vinculos
        cursor.execute("""
            CREATE TABLE vinculos_pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                tipo_vinculo TEXT NOT NULL CHECK(tipo_vinculo IN ('clinica', 'veterinario', 'tutor')),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                data_desativacao TIMESTAMP NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                UNIQUE(pet_id, usuario_id, tipo_vinculo)
            )
        """)

        # Cria índice para performance
        cursor.execute("CREATE INDEX idx_vinculos_pet_usuario ON vinculos_pets(pet_id, usuario_id)")
        cursor.execute("CREATE INDEX idx_vinculos_usuario_pet ON vinculos_pets(usuario_id, pet_id)")

        conn.commit()
        conn.close()
        logger.info("Tabela 'vinculos_pets' criada")
        print("✅ Tabela 'vinculos_pets' criada")
        return True

    except Exception as e:
        logger.error(f"Erro ao criar vinculos_pets: {e}")
        return False


def criar_tabela_notificacoes():
    """Cria tabela para notificações de dor"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se tabela já existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notificacoes'")
        if cursor.fetchone():
            print("✅ Tabela 'notificacoes' já existe")
            conn.close()
            return True

        # Cria tabela de notificações
        cursor.execute("""
            CREATE TABLE notificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                usuario_id_destino INTEGER NOT NULL,
                tipo_notificacao TEXT NOT NULL CHECK(tipo_notificacao IN ('dor_detectada', 'avaliacao_concluida', 'vinculo_criado')),
                nivel_prioridade INTEGER DEFAULT 1 CHECK(nivel_prioridade IN (1, 2, 3)),
                mensagem TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                lida BOOLEAN DEFAULT 0,
                data_lida NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id_destino) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Cria índices
        cursor.execute("CREATE INDEX idx_notif_usuario ON notificacoes(usuario_id_destino)")
        cursor.execute("CREATE INDEX idx_notif_pet ON notificacoes(pet_id)")
        cursor.execute("CREATE INDEX idx_notif_nao_lida ON notificacoes(usuario_id_destino, lida) WHERE lida = 0")

        conn.commit()
        conn.close()
        logger.info("Tabela 'notificacoes' criada")
        print("✅ Tabela 'notificacoes' criada")
        return True

    except Exception as e:
        logger.error(f"Erro ao criar notificacoes: {e}")
        return False


def adicionar_campo_link_compartilhamento():
    """Adiciona campo para link de compartilhamento nos pets"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(pets)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'link_compartilhamento' not in colunas:
            cursor.execute("""
                ALTER TABLE pets 
                ADD COLUMN link_compartilhamento TEXT UNIQUE
            """)
            cursor.execute("""
                ALTER TABLE pets 
                ADD COLUMN link_expiracao TIMESTAMP NULL
            """)
            logger.info("Campos de compartilhamento adicionados")
            print("✅ Campos 'link_compartilhamento' e 'link_expiracao' adicionados")
        else:
            print("✅ Campos de compartilhamento já existem")

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Erro ao adicionar campos de compartilhamento: {e}")
        return False


def migrar_banco_completo():
    """Executa todas as migrações"""
    print("🔄 Executando migrações completas do PETDor...")

    sucessos = []
    falhas = []

    # Migrações existentes (se você já tem)
    try:
        from . import adicionar_colunas_desativacao, adicionar_campo_admin
        sucessos.append("Migrações existentes")
    except:
        pass

    # Novas migrações
    if adicionar_campo_tipo_usuario():
        sucessos.append("tipo_usuario")
    else:
        falhas.append("tipo_usuario")

    if criar_tabela_vinculos_pets():
        sucessos.append("vinculos_pets")
    else:
        falhas.append("vinculos_pets")

    if criar_tabela_notificacoes():
        sucessos.append("notificacoes")
    else:
        falhas.append("notificacoes")

    if adicionar_campo_link_compartilhamento():
        sucessos.append("link_compartilhamento")
    else:
        falhas.append("link_compartilhamento")

    print(f"✅ Migrações concluídas: {len(sucessos)} sucessos")
    if falhas:
        print(f"❌ Falhas: {', '.join(falhas)}")
    else:
        print("🎉 Todas as migrações executadas com sucesso!")

    return len(falhas) == 0


if __name__ == "__main__":
    migrar_banco_completo()
