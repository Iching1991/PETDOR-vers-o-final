"""
Funções de consulta de dados do PETDOR
"""

import logging
from .connection import conectar_db

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# 👤 Buscar usuário por ID
# ---------------------------------------------------------
def buscar_usuario_por_id(usuario_id: int):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo
            FROM usuarios
            WHERE id = ?
        """, (usuario_id,))

        row = cursor.fetchone()
        return dict(row) if row else None

    except Exception as e:
        logger.error(f"[ERRO] buscar_usuario_por_id: {e}")
        return None

    finally:
        if conn:
            conn.close()


# ---------------------------------------------------------
# 🔎 Buscar usuário por email
# ---------------------------------------------------------
def buscar_usuario_por_email(email: str):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo
            FROM usuarios
            WHERE LOWER(email) = LOWER(?)
        """, (email.strip(),))

        row = cursor.fetchone()
        return dict(row) if row else None

    except Exception as e:
        logger.error(f"[ERRO] buscar_usuario_por_email: {e}")
        return None

    finally:
        if conn:
            conn.close()


# ---------------------------------------------------------
# 📜 Listar todos os usuários (para admin)
# ---------------------------------------------------------
def listar_usuarios():
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo
            FROM usuarios
            ORDER BY data_criacao DESC
        """)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except Exception as e:
        logger.error(f"[ERRO] listar_usuarios: {e}")
        return []

    finally:
        if conn:
            conn.close()
