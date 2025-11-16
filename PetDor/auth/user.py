# auth/user.py

import sqlite3
import bcrypt
from utils.validators import validar_email, validar_senha, validar_nome, senhas_conferem
from config import DATABASE_PATH

def conectar_db():
    return sqlite3.connect(DATABASE_PATH)

def cadastrar_usuario(nome: str, email: str, senha: str, confirmar_senha: str) -> tuple[bool, str]:
    # Valida nome
    valido, msg = validar_nome(nome)
    if not valido:
        return False, msg

    # Valida email
    valido, msg = validar_email(email)
    if not valido:
        return False, msg

    # Valida senha
    valido, msg = validar_senha(senha)
    if not valido:
        return False, msg

    # Confere senha
    valido, msg = senhas_conferem(senha, confirmar_senha)
    if not valido:
        return False, msg

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se já existe email cadastrado
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Este e-mail já está cadastrado."

        # Hash da senha
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

        # Insere usuário
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome, email, senha_hash)
        )
        conn.commit()
        return True, "Usuário cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar usuário: {e}"
    finally:
        conn.close()


def autenticar(email: str, senha: str) -> tuple[bool, dict | str]:
    """
    Retorna (True, usuario_dict) se autenticado, ou (False, mensagem) se falhar
    """
    # Valida email
    valido, msg = validar_email(email)
    if not valido:
        return False, msg

    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        if not row:
            return False, "Usuário não encontrado."

        id_usuario, nome, email_db, senha_hash = row

        if not bcrypt.checkpw(senha.encode(), senha_hash):
            return False, "Senha incorreta."

        usuario = {"id": id_usuario, "nome": nome, "email": email_db}
        return True, usuario

    except Exception as e:
        return False, f"Erro ao autenticar: {e}"
    finally:
        conn.close()


    except Exception as e:
        logger.error(f"Erro ao excluir usuário: {e}")
        return False, "Erro ao excluir conta. Tente novamente."

