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
            print("✅ Banco de dados já está atualizado!")

        return True

    except Exception as e:
        logger.error(f"Erro na migração: {e}")
        print(f"❌ Erro na migração: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Iniciando migração do banco de dados...")
    adicionar_colunas_desativacao()
