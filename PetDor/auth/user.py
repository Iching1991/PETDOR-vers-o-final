"""
Gerenciamento de usuários e autenticação
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import sqlite3
import bcrypt
import logging
from datetime import datetime
from utils.validators import validar_email, validar_senha, validar_nome, senhas_conferem

logger = logging.getLogger(__name__)

def conectar_db():
    """Conecta ao banco de dados"""
    from config import DATABASE_PATH
    return sqlite3.connect(DATABASE_PATH)

def cadastrar_usuario(nome, email, senha, confirmar_senha):
    """Cadastra um novo usuário"""
    # Validações
    for func, valor in [(validar_nome, nome), (validar_email, email), (validar_senha, senha)]:
        ok, msg = func(valor)
        if not ok:
            return False, msg

    ok, msg = senhas_conferem(senha, confirmar_senha)
    if not ok:
        return False, msg

    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Este e-mail já está cadastrado."

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo) VALUES (?, ?, ?, ?, ?)",
            (nome, email, senha_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        )
        conn.commit()
        logger.info(f"Usuário cadastrado: {email}")
        return True, "Usuário cadastrado com sucesso!"
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}")
        return False, f"Erro ao cadastrar usuário: {e}"
    finally:
        conn.close()

def autenticar_usuario(email, senha):
    """Autentica um usuário"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, senha_hash, ativo FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return False, "Email ou senha incorretos", None

        if not usuario[3]:  # ativo
            return False, "Conta desativada", None

        if bcrypt.checkpw(senha.encode('utf-8'), usuario[2]):
            logger.info(f"Usuário autenticado: {email}")
            return True, f"Bem-vindo, {usuario[1]}!", usuario[0]
        else:
            return False, "Email ou senha incorretos", None

    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return False, "Erro na autenticação", None
    finally:
        conn.close()

def buscar_usuario_por_id(usuario_id):
    """Busca dados do usuário por ID"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, data_criacao FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()

        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'data_criacao': row[3]
            }
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return None
    finally:
        conn.close()

def atualizar_usuario(usuario_id, nome=None, email=None):
    """
    Atualiza dados do usuário

    Args:
        usuario_id: ID do usuário
        nome: Novo nome (opcional)
        email: Novo email (opcional)

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Validações
        if nome:
            ok, msg = validar_nome(nome)
            if not ok:
                return False, msg

        if email:
            ok, msg = validar_email(email)
            if not ok:
                return False, msg

        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
        if not cursor.fetchone():
            return False, "Usuário não encontrado"

        # Atualiza campos fornecidos
        if nome and email:
            cursor.execute(
                "UPDATE usuarios SET nome = ?, email = ? WHERE id = ?",
                (nome, email, usuario_id)
            )
        elif nome:
            cursor.execute(
                "UPDATE usuarios SET nome = ? WHERE id = ?",
                (nome, usuario_id)
            )
        elif email:
            cursor.execute(
                "UPDATE usuarios SET email = ? WHERE id = ?",
                (email, usuario_id)
            )
        else:
            return False, "Nenhum campo para atualizar"

        conn.commit()
        logger.info(f"Usuário {usuario_id} atualizado")
        return True, "Dados atualizados com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        return False, f"Erro ao atualizar usuário: {e}"
    finally:
        conn.close()

def alterar_senha(usuario_id, senha_atual, nova_senha, confirmar_senha):
    """
    Altera a senha do usuário

    Args:
        usuario_id: ID do usuário
        senha_atual: Senha atual para validação
        nova_senha: Nova senha
        confirmar_senha: Confirmação da nova senha

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Validações
        ok, msg = validar_senha(nova_senha)
        if not ok:
            return False, msg

        ok, msg = senhas_conferem(nova_senha, confirmar_senha)
        if not ok:
            return False, msg

        conn = conectar_db()
        cursor = conn.cursor()

        # Busca senha atual
        cursor.execute("SELECT senha_hash FROM usuarios WHERE id = ?", (usuario_id,))
        resultado = cursor.fetchone()

        if not resultado:
            return False, "Usuário não encontrado"

        # Verifica senha atual
        if not bcrypt.checkpw(senha_atual.encode('utf-8'), resultado[0]):
            return False, "Senha atual incorreta"

        # Atualiza senha
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (nova_senha_hash, usuario_id)
        )

        conn.commit()
        logger.info(f"Senha alterada para usuário {usuario_id}")
        return True, "Senha alterada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return False, f"Erro ao alterar senha: {e}"
    finally:
        conn.close()

def deletar_usuario(usuario_id, senha):
    """
    Desativa a conta do usuário (soft delete) e registra data/motivo.

    Não deleta fisicamente do banco - apenas marca como inativo
    e registra quando e por quê foi desativado para fins de auditoria.

    Args:
        usuario_id: ID do usuário
        senha: Senha para confirmação

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Busca senha e email
        cursor.execute(
            "SELECT senha_hash, email FROM usuarios WHERE id = ?",
            (usuario_id,)
        )
        resultado = cursor.fetchone()

        if not resultado:
            return False, "Usuário não encontrado"

        senha_hash, email = resultado

        # Verifica senha
        if not bcrypt.checkpw(senha.encode("utf-8"), senha_hash):
            return False, "Senha incorreta"

        # Marca como inativo + registra data e motivo
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        motivo = "Autoexclusão pelo usuário"

        cursor.execute(
            """
            UPDATE usuarios
               SET ativo = 0,
                   data_desativacao = ?,
                   motivo_desativacao = ?
             WHERE id = ?
            """,
            (agora, motivo, usuario_id),
        )

        conn.commit()
        logger.info(f"Conta desativada: {email} em {agora}")
        return True, "Conta desativada com sucesso"

    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {e}")
        return False, f"Erro ao deletar usuário: {e}"
    finally:
        conn.close()
