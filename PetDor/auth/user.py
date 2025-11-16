"""
Gerenciamento de usuários: cadastro e autenticação
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import sqlite3
import bcrypt
from datetime import datetime
from typing import Tuple
from utils.validators import validar_email, validar_senha, validar_nome, senhas_conferem
from config import DATABASE_PATH


def conectar_db():
    """Cria conexão com o banco de dados"""
    return sqlite3.connect(DATABASE_PATH)


def cadastrar_usuario(nome: str, email: str, senha: str, confirmar_senha: str) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário no sistema

    Args:
        nome: Nome completo do usuário
        email: Email do usuário
        senha: Senha do usuário
        confirmar_senha: Confirmação da senha

    Returns:
        Tupla (sucesso, mensagem)
    """
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

        # Verifica se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email.strip().lower(),))
        if cursor.fetchone():
            return False, "Este e-mail já está cadastrado."

        # Hash da senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        # Insere usuário
        cursor.execute(
            """INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo) 
               VALUES (?, ?, ?, ?, ?)""",
            (nome.strip(), email.strip().lower(), senha_hash, 
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1)
        )
        conn.commit()

        return True, "Usuário cadastrado com sucesso!"

    except Exception as e:
        return False, f"Erro ao cadastrar usuário: {str(e)}"
    finally:
        conn.close()


def autenticar_usuario(email: str, senha: str) -> Tuple[bool, str, int]:
    """
    Autentica um usuário

    Args:
        email: Email do usuário
        senha: Senha do usuário

    Returns:
        Tupla (sucesso, mensagem, usuario_id)
    """
    if not email or not senha:
        return False, "Email e senha são obrigatórios", 0

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, senha_hash, ativo FROM usuarios WHERE email = ?",
            (email.strip().lower(),)
        )

        resultado = cursor.fetchone()

        if not resultado:
            return False, "Email ou senha incorretos", 0

        usuario_id, senha_hash, ativo = resultado

        if not ativo:
            return False, "Conta desativada. Entre em contato com o suporte.", 0

        # Verifica senha
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
            return True, "Login realizado com sucesso!", usuario_id
        else:
            return False, "Email ou senha incorretos", 0

    except Exception as e:
        return False, f"Erro ao autenticar: {str(e)}", 0
    finally:
        conn.close()


def buscar_usuario_por_email(email: str) -> dict:
    """
    Busca usuário por email

    Args:
        email: Email do usuário

    Returns:
        Dicionário com dados do usuário ou None
    """
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nome, email, data_criacao FROM usuarios WHERE email = ? AND ativo = 1",
            (email.strip().lower(),)
        )

        resultado = cursor.fetchone()

        if resultado:
            return dict(resultado)
        return None

    except Exception:
        return None
    finally:
        conn.close()


def atualizar_senha(usuario_id: int, nova_senha: str) -> Tuple[bool, str]:
    """
    Atualiza a senha de um usuário

    Args:
        usuario_id: ID do usuário
        nova_senha: Nova senha

    Returns:
        Tupla (sucesso, mensagem)
    """
    ok, msg = validar_senha(nova_senha)
    if not ok:
        return False, msg

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())

        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (senha_hash, usuario_id)
        )

        conn.commit()

        if cursor.rowcount > 0:
            return True, "Senha atualizada com sucesso!"
        else:
            return False, "Usuário não encontrado"

    except Exception as e:
        return False, f"Erro ao atualizar senha: {str(e)}"
    finally:
        conn.close()
