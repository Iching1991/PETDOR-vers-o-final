"""
Gerenciamento de recuperação e redefinição de senha
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import sqlite3
import secrets
from datetime import datetime, timedelta
from typing import Tuple
from config import DATABASE_PATH
from auth.user import buscar_usuario_por_email, atualizar_senha
from utils.validators import validar_email, validar_senha, senhas_conferem


def conectar_db():
    """Cria conexão com o banco de dados"""
    return sqlite3.connect(DATABASE_PATH)


def gerar_token() -> str:
    """Gera um token seguro para reset de senha"""
    return secrets.token_urlsafe(32)


def solicitar_reset(email: str) -> Tuple[bool, str]:
    """
    Solicita reset de senha para um email

    Args:
        email: Email do usuário

    Returns:
        Tupla (sucesso, mensagem)
    """
    ok, msg = validar_email(email)
    if not ok:
        return False, msg

    # Busca usuário
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        # Por segurança, não revela se o email existe ou não
        return True, "Se o email estiver cadastrado, você receberá um link de recuperação."

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Gera token
        token = gerar_token()
        expires_at = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Salva token
        cursor.execute(
            """INSERT INTO password_resets (usuario_id, token, expires_at, created_at, used)
               VALUES (?, ?, ?, ?, 0)""",
            (usuario['id'], token, expires_at, created_at)
        )

        conn.commit()

        # TODO: Enviar email com o link
        # Link seria algo como: https://seuapp.com/reset_senha?token={token}
        print(f"[DEBUG] Token de reset: {token}")  # Remover em produção

        return True, "Se o email estiver cadastrado, você receberá um link de recuperação."

    except Exception as e:
        return False, f"Erro ao solicitar reset: {str(e)}"
    finally:
        conn.close()


def validar_token(token: str) -> Tuple[bool, str]:
    """
    Valida se um token é válido e não expirou

    Args:
        token: Token de reset

    Returns:
        Tupla (válido, mensagem)
    """
    if not token:
        return False, "Token inválido"

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, usuario_id, expires_at, used 
               FROM password_resets 
               WHERE token = ?""",
            (token,)
        )

        resultado = cursor.fetchone()

        if not resultado:
            return False, "Token inválido ou expirado"

        reset_id, usuario_id, expires_at, used = resultado

        if used:
            return False, "Este token já foi utilizado"

        # Verifica expiração
        expires_datetime = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_datetime:
            return False, "Token expirado. Solicite um novo link."

        return True, "Token válido"

    except Exception as e:
        return False, f"Erro ao validar token: {str(e)}"
    finally:
        conn.close()


def redefinir_senha(token: str, nova_senha: str, confirmar_senha: str) -> Tuple[bool, str]:
    """
    Redefine a senha usando um token válido

    Args:
        token: Token de reset
        nova_senha: Nova senha
        confirmar_senha: Confirmação da senha

    Returns:
        Tupla (sucesso, mensagem)
    """
    # Valida token
    valido, msg = validar_token(token)
    if not valido:
        return False, msg

    # Valida senha
    ok, msg = validar_senha(nova_senha)
    if not ok:
        return False, msg

    ok, msg = senhas_conferem(nova_senha, confirmar_senha)
    if not ok:
        return False, msg

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Busca usuario_id do token
        cursor.execute(
            "SELECT usuario_id FROM password_resets WHERE token = ? AND used = 0",
            (token,)
        )

        resultado = cursor.fetchone()

        if not resultado:
            return False, "Token inválido"

        usuario_id = resultado[0]

        # Atualiza senha
        sucesso, msg = atualizar_senha(usuario_id, nova_senha)

        if not sucesso:
            return False, msg

        # Marca token como usado
        cursor.execute(
            "UPDATE password_resets SET used = 1 WHERE token = ?",
            (token,)
        )

        conn.commit()

        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        return False, f"Erro ao redefinir senha: {str(e)}"
    finally:
        conn.close()

