"""
Gerenciamento de usuários do PETDOR
"""

import bcrypt
import logging
from datetime import datetime
from database.connection import conectar_db

logger = logging.getLogger(__name__)

# -------------------------------
# Usuário
# -------------------------------
def cadastrar_usuario(nome, email, senha, confirmar=None):
    """Cadastra um novo usuário"""
    if confirmar and senha != confirmar:
        return False, "As senhas não conferem"

    if len(senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres"

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM usuarios WHERE email = ?", (email.lower().strip(),))
    if cur.fetchone():
        conn.close()
        return False, "Este email já está cadastrado"

    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo) VALUES (?, ?, ?, ?, 1)",
        (nome.strip().title(), email.lower().strip(), senha_hash, data_criacao)
    )

    conn.commit()
    conn.close()
    logger.info(f"Usuário cadastrado: {email}")
    return True, "Conta criada com sucesso!"

# -------------------------------
# Autenticação
# -------------------------------
def autenticar_usuario(email, senha):
    """Autentica um usuário"""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nome, senha_hash, ativo FROM usuarios WHERE email = ?",
        (email.lower().strip(),)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return False, "Email ou senha incorretos", None

    usuario_id, nome, senha_hash, ativo = row
    if not ativo:
        return False, "Conta desativada", None

    if bcrypt.checkpw(senha.encode(), senha_hash):
        return True, f"Bem-vindo(a), {nome}!", usuario_id
    else:
        return False, "Email ou senha incorretos", None
