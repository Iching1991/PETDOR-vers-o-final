"""
Sistema de confirmação de email
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import sqlite3
import secrets
import logging
from datetime import datetime, timedelta
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def conectar_db():
    """Conecta ao banco de dados"""
    return sqlite3.connect(DATABASE_PATH)


def gerar_token_confirmacao(usuario_id, email):
    """
    Gera token de confirmação de email

    Args:
        usuario_id: ID do usuário
        email: Email do usuário

    Returns:
        Tupla (sucesso, token)
    """
    try:
        # Gera token único de 32 bytes (URL-safe)
        token = secrets.token_urlsafe(32)

        # Define expiração (24 horas)
        expiracao = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

        conn = conectar_db()
        cursor = conn.cursor()

        # Salva token no banco
        cursor.execute("""
            UPDATE usuarios 
            SET token_confirmacao = ?, data_expiracao_token = ?
            WHERE id = ?
        """, (token, expiracao, usuario_id))

        conn.commit()
        conn.close()

        logger.info(f"Token de confirmação gerado para usuário {usuario_id}")
        return True, token

    except Exception as e:
        logger.error(f"Erro ao gerar token: {e}")
        return False, None


def validar_token_confirmacao(token):
    """
    Valida token de confirmação

    Args:
        token: Token de confirmação

    Returns:
        Tupla (valido, usuario_id, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Busca usuário pelo token
        cursor.execute("""
            SELECT id, email, email_confirmado, data_expiracao_token
            FROM usuarios
            WHERE token_confirmacao = ?
        """, (token,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, None, "Token inválido ou não encontrado"

        usuario_id, email, email_confirmado, expiracao = row

        # Verifica se já foi confirmado
        if email_confirmado:
            conn.close()
            return False, None, "Email já confirmado anteriormente"

        # Verifica expiração
        if expiracao:
            expiracao_dt = datetime.strptime(expiracao, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expiracao_dt:
                conn.close()
                return False, None, "Token expirado. Solicite um novo email de confirmação"

        conn.close()
        return True, usuario_id, "Token válido"

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return False, None, f"Erro ao validar token: {e}"


def confirmar_email(usuario_id):
    """
    Confirma o email do usuário

    Args:
        usuario_id: ID do usuário

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Marca email como confirmado e remove token
        cursor.execute("""
            UPDATE usuarios 
            SET email_confirmado = 1, 
                token_confirmacao = NULL, 
                data_expiracao_token = NULL
            WHERE id = ?
        """, (usuario_id,))

        afetados = cursor.rowcount

        conn.commit()
        conn.close()

        if afetados > 0:
            logger.info(f"Email confirmado para usuário {usuario_id}")
            return True, "Email confirmado com sucesso!"
        else:
            return False, "Usuário não encontrado"

    except Exception as e:
        logger.error(f"Erro ao confirmar email: {e}")
        return False, f"Erro ao confirmar email: {e}"


def reenviar_email_confirmacao(email):
    """
    Reenvia email de confirmação

    Args:
        email: Email do usuário

    Returns:
        Tupla (sucesso, mensagem, usuario_id, token)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Busca usuário
        cursor.execute("""
            SELECT id, nome, email_confirmado
            FROM usuarios
            WHERE email = ? AND ativo = 1
        """, (email,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Email não encontrado", None, None

        usuario_id, nome, email_confirmado = row

        if email_confirmado:
            conn.close()
            return False, "Este email já foi confirmado", None, None

        conn.close()

        # Gera novo token
        sucesso, token = gerar_token_confirmacao(usuario_id, email)

        if sucesso:
            return True, "Novo email de confirmação será enviado", usuario_id, token
        else:
            return False, "Erro ao gerar novo token", None, None

    except Exception as e:
        logger.error(f"Erro ao reenviar confirmação: {e}")
        return False, f"Erro: {e}", None, None


def buscar_usuario_por_token(token):
    """
    Busca dados do usuário pelo token de confirmação

    Args:
        token: Token de confirmação

    Returns:
        Dict com dados do usuário ou None
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, tipo_usuario
            FROM usuarios
            WHERE token_confirmacao = ?
        """, (token,))

        row = cursor.fetchone()

        if row:
            usuario = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'tipo_usuario': row[3] or 'tutor'
            }
            conn.close()
            return usuario

        conn.close()
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuário por token: {e}")
        return None


def verificar_email_confirmado(email):
    """
    Verifica se um email já foi confirmado

    Args:
        email: Email a verificar

    Returns:
        Boolean
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT email_confirmado
            FROM usuarios
            WHERE email = ?
        """, (email,))

        row = cursor.fetchone()
        conn.close()

        return bool(row and row[0])

    except Exception as e:
        logger.error(f"Erro ao verificar email: {e}")
        return False
