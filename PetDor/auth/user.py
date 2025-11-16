# auth/user.py

import sqlite3
import bcrypt
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path ANTES de qualquer importação local
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Agora sim, importe os módulos locais
from utils.validators import validar_email, validar_senha, validar_nome, senhas_conferem
from config import DATABASE_PATH


def conectar_db():
    return sqlite3.connect(DATABASE_PATH)

def cadastrar_usuario(nome, email, senha, confirmar_senha):
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

        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
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
