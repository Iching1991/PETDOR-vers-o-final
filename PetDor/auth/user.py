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
        return False, f"Erro ao cadastrar usuário: {e}"  # ← CORRIGIDO AQUI
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
