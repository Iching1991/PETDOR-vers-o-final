# PetDor/auth/user.py
"""
Gerenciamento de usuários
"""

import logging
from datetime import datetime
import bcrypt
from connection import conectar_db

logger = logging.getLogger(__name__)

def cadastrar_usuario(nome, email, senha, confirmar_senha):
    """Cadastra um novo usuário"""
    try:
        if not all([nome, email, senha, confirmar_senha]):
            return False, "Preencha todos os campos obrigatórios"

        if senha != confirmar_senha:
            return False, "As senhas não conferem"

        if len(senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres"

        nome = nome.strip().title()
        email = email.strip().lower()
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cur.fetchone():
            conn.close()
            return False, "Este email já está cadastrado"

        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo)
            VALUES (?, ?, ?, ?, 1)
        """, (nome, email, senha_hash, data_criacao))
        conn.commit()
        conn.close()
        logger.info(f"Usuário cadastrado: {email}")
        return True, "Conta criada com sucesso!"
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}")
        return False, f"Erro ao criar conta: {e}"

def autenticar_usuario(email, senha):
    """Autentica usuário"""
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, senha_hash, ativo FROM usuarios WHERE email = ?", (email.lower().strip(),))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False, "Email ou senha incorretos", None
        usuario_id, nome, senha_hash, ativo = row
        if not ativo:
            conn.close()
            return False, "Conta desativada", None
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
            conn.close()
            return True, f"Bem-vindo(a), {nome}!", usuario_id
        conn.close()
        return False, "Email ou senha incorretos", None
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return False, "Erro ao fazer login", None
