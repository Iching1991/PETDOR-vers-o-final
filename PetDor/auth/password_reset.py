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
import string
from datetime import datetime, timedelta
import logging
from utils.email_sender import enviar_email_reset

logger = logging.getLogger(__name__)

def conectar_db():
    """Conecta ao banco de dados"""
    from config import DATABASE_PATH
    return sqlite3.connect(DATABASE_PATH)

def gerar_token_seguro(tamanho=32):
    """Gera um token criptograficamente seguro"""
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(tamanho))

def solicitar_reset(email):
    """Solicita reset de senha"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se email existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        if not usuario:
            return False, "Email não encontrado"

        # Remove tokens antigos do usuário
        cursor.execute("DELETE FROM password_resets WHERE usuario_id = ?", (usuario[0],))

        # Gera novo token
        token = gerar_token_seguro()
        expires_at = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Salva token
        cursor.execute(
            "INSERT INTO password_resets (usuario_id, token, expires_at, used, created_at) VALUES (?, ?, ?, ?, ?)",
            (usuario[0], token, expires_at, 0, created_at)
        )
        conn.commit()

        # Envia email
        sucesso_email, msg_email = enviar_email_reset(email, token)
        if not sucesso_email:
            logger.warning(f"Falha ao enviar email para {email}: {msg_email}")
            # Mesmo assim retorna sucesso para não revelar se email existe
            return True, "Se o email existir, você receberá instruções para redefinir a senha"

        logger.info(f"Token de reset gerado para: {email}")
        return True, "Se o email existir, você receberá instruções para redefinir a senha"

    except Exception as e:
        logger.error(f"Erro ao solicitar reset: {e}")
        return False, "Erro ao processar solicitação"
    finally:
        conn.close()

def validar_token(token):
    """Valida se o token é válido e não expirou"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT usuario_id, expires_at, used 
            FROM password_resets 
            WHERE token = ? AND used = 0
        """, (token,))

        reset = cursor.fetchone()
        if not reset:
            return False, "Token inválido ou já utilizado"

        expires_at = datetime.strptime(reset[1], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_at:
            return False, "Token expirado"

        return True, "", reset[0]  # Retorna True, mensagem vazia e usuario_id

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return False, "Erro ao validar token"
    finally:
        conn.close()

def redefinir_senha(token, nova_senha, confirmar_senha):
    """Redefine a senha do usuário"""
    from utils.validators import validar_senha, senhas_conferem

    # Valida senhas
    ok, msg = validar_senha(nova_senha)
    if not ok:
        return False, msg

    ok, msg = senhas_conferem(nova_senha, confirmar_senha)
    if not ok:
        return False, msg

    try:
        # Valida token
        valido, msg_token, usuario_id = validar_token(token)
        if not valido:
            return False, msg_token

        conn = conectar_db()
        cursor = conn.cursor()

        # Hash da nova senha
        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())

        # Atualiza senha e marca token como usado
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (senha_hash, usuario_id)
        )
        cursor.execute(
            "UPDATE password_resets SET used = 1 WHERE token = ?",
            (token,)
        )

        conn.commit()
        logger.info(f"Senha redefinida para usuário ID: {usuario_id}")
        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        return False, "Erro ao redefinir senha"
    finally:
        conn.close()
