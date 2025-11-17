"""
Funções de autenticação e cadastro
"""
from database.connection import conectar_db
import bcrypt
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def cadastrar_usuario(nome, email, senha, confirmar_senha):
    try:
        if senha != confirmar_senha:
            return False, "Senhas não conferem"
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return False, "Email já cadastrado"
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (?, ?, ?)
        """, (nome.strip(), email.lower().strip(), senha_hash))
        conn.commit()
        conn.close()
        return True, "Conta criada com sucesso!"
    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return False, str(e)

def autenticar_usuario(email, senha):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, senha_hash, ativo FROM usuarios WHERE email = ?
        """, (email.lower().strip(),))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return False, "Email ou senha incorretos", None
        usuario_id, nome, senha_hash, ativo = row
        if not ativo:
            return False, "Conta desativada", None
        if bcrypt.checkpw(senha.encode(), senha_hash):
            return True, f"Bem-vindo, {nome}!", usuario_id
        return False, "Email ou senha incorretos", None
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return False, "Erro ao autenticar", None
