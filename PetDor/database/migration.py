"""
Script de migração do banco de dados
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
    """
    Adiciona colunas para rastrear desativação de contas
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Verifica se as colunas já existem
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]

        mudancas = []

        if 'data_desativacao' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN data_desativacao TEXT")
            mudancas.append("data_desativacao")
            logger.info("Coluna 'data_desativacao' adicionada")

        if 'motivo_desativacao' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN motivo_desativacao TEXT")
            mudancas.append("motivo_desativacao")
            logger.info("Coluna 'motivo_desativacao' adicionada")

        conn.commit()
        conn.close()

        if mudancas:
            print(f"✅ Migração concluída! Colunas adicionadas: {', '.join(mudancas)}")
        else:
            print("✅ Colunas de desativação já existem")

        return True

    except Exception as e:
        logger.error(f"Erro na migração de colunas de desativação: {e}")
        print(f"❌ Erro na migração: {e}")
        return False


def adicionar_campo_admin():
    """Adiciona campo is_admin para controle de acesso"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Verifica se a coluna já existe
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'is_admin' not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0")
            logger.info("Coluna 'is_admin' adicionada")

            # Define o primeiro usuário como admin (opcional)
            cursor.execute("""
                UPDATE usuarios 
                SET is_admin = 1 
                WHERE id = (SELECT MIN(id) FROM usuarios)
            """)
            logger.info("Primeiro usuário definido como admin")
            print("✅ Campo 'is_admin' adicionado e primeiro usuário definido como admin")
        else:
            print("✅ Campo 'is_admin' já existe")

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Erro ao adicionar campo admin: {e}")
        print(f"❌ Erro ao adicionar campo admin: {e}")
        return False


def migrar_banco_completo():
    """Executa todas as migrações"""
    print("🔄 Executando migrações completas...")
    adicionar_colunas_desativacao()
    adicionar_campo_admin()
    print("✅ Todas as migrações concluídas!")


if __name__ == "__main__":
    migrar_banco_completo()
