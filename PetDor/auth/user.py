"""
Gerenciamento de usuários do PETDOR
"""

import logging
import bcrypt
from datetime import datetime
from connection import conectar_db

logger = logging.getLogger(__name__)

# -------------------------------
# CADASTRO DE USUÁRIO
# -------------------------------
def cadastrar_usuario(nome, email, senha, confirmar_senha, tipo_usuario="tutor"):
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
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Este email já está cadastrado"

        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo)
            VALUES (?, ?, ?, ?, 1)
        """, (nome, email, senha_hash, data_criacao))

        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Usuário cadastrado: {email} (ID: {usuario_id})")
        return True, "Conta criada com sucesso!"

    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return False, f"Erro ao criar conta: {str(e)}"

# -------------------------------
# AUTENTICAÇÃO
# -------------------------------
def autenticar_usuario(email, senha):
    """Autentica um usuário"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, senha_hash, ativo
            FROM usuarios
            WHERE email = ?
        """, (email.lower().strip(),))

        row = cursor.fetchone()
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
        else:
            conn.close()
            return False, "Email ou senha incorretos", None

    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return False, "Erro ao fazer login", None

# -------------------------------
# BUSCA DE USUÁRIOS
# -------------------------------
def buscar_usuario_por_id(usuario_id):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, data_criacao, ativo FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'data_criacao': row[3],
                'ativo': bool(row[4])
            }
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return None

def buscar_usuario_por_email(email):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email, ativo FROM usuarios WHERE email = ?", (email.lower().strip(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'ativo': bool(row[3])
            }
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por email: {e}")
        return None

