"""
Funções de consulta de dados
"""
from .connection import conectar_db
import logging

logger = logging.getLogger(__name__)

def buscar_usuario_por_id(usuario_id):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo
            FROM usuarios
            WHERE id = ?
        """, (usuario_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "nome": row[1],
                "email": row[2],
                "data_criacao": row[3],
                "ativo": bool(row[4])
            }
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuario: {e}")
        return None

def buscar_usuario_por_email(email):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, email, ativo
            FROM usuarios
            WHERE email = ?
        """, (email.lower().strip(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "nome": row[1],
                "email": row[2],
                "ativo": bool(row[3])
            }
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuario por email: {e}")
        return None
