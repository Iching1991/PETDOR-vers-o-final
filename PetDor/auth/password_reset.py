"""
Gerenciamento de tokens de reset de senha
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

logger = logging.getLogger(__name__)


def conectar_db():
    """Conecta ao banco de dados"""
    from config import DATABASE_PATH
    return sqlite3.connect(DATABASE_PATH)


def buscar_usuario_por_email(email):
    """
    Busca usuário por email

    Args:
        email: Email do usuário

    Returns:
        Dicionário com dados do usuário ou None
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, ativo 
            FROM usuarios 
            WHERE email = ?
        """, (email,))

        row = cursor.fetchone()

        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'ativo': row[3]
            }
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuário por email: {e}")
        return None
    finally:
        conn.close()


def criar_token_reset(usuario_id):
    """
    Cria um token de reset de senha

    Args:
        usuario_id: ID do usuário

    Returns:
        Tupla (sucesso, token)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Gera token único
        token = secrets.token_urlsafe(32)

        # Calcula data de expiração (1 hora)
        expiracao = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        # Salva token no banco
        cursor.execute("""
            INSERT INTO tokens_reset (usuario_id, token, expiracao, usado)
            VALUES (?, ?, ?, 0)
        """, (usuario_id, token, expiracao))

        conn.commit()

        logger.info(f"Token de reset criado para usuário {usuario_id}")
        return True, token

    except Exception as e:
        logger.error(f"Erro ao criar token de reset: {e}")
        return False, None
    finally:
        conn.close()


def validar_token_reset(token):
    """
    Valida um token de reset

    Args:
        token: Token a ser validado

    Returns:
        Tupla (válido, usuario_id, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT usuario_id, expiracao, usado
            FROM tokens_reset
            WHERE token = ?
        """, (token,))

        row = cursor.fetchone()

        if not row:
            return False, None, "Token inválido"

        usuario_id, expiracao, usado = row

        if usado:
            return False, None, "Token já foi utilizado"

        # Verifica expiração
        expiracao_dt = datetime.strptime(expiracao, "%Y-%m-%d %H:%M:%S")

        if datetime.now() > expiracao_dt:
            return False, None, "Token expirado"

        return True, usuario_id, "Token válido"

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return False, None, "Erro ao validar token"
    finally:
        conn.close()


def marcar_token_usado(token):
    """
    Marca um token como usado

    Args:
        token: Token a ser marcado

    Returns:
        bool: Sucesso da operação
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tokens_reset
            SET usado = 1
            WHERE token = ?
        """, (token,))

        conn.commit()

        logger.info(f"Token marcado como usado")
        return True

    except Exception as e:
        logger.error(f"Erro ao marcar token como usado: {e}")
        return False
    finally:
        conn.close()


def redefinir_senha(usuario_id, nova_senha):
    """
    Redefine a senha do usuário

    Args:
        usuario_id: ID do usuário
        nova_senha: Nova senha

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        import bcrypt

        conn = conectar_db()
        cursor = conn.cursor()

        # Hash da nova senha
        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())

        # Atualiza senha
        cursor.execute("""
            UPDATE usuarios
            SET senha_hash = ?
            WHERE id = ?
        """, (senha_hash, usuario_id))

        conn.commit()

        logger.info(f"Senha redefinida para usuário {usuario_id}")
        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        return False, f"Erro ao redefinir senha: {e}"
    finally:
        conn.close()
