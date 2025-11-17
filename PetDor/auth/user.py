"""
Gerenciamento de usuarios do PETDor
"""
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import sqlite3
import bcrypt
import logging
from datetime import datetime
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def conectar_db():
    """Conecta ao banco de dados"""
    return sqlite3.connect(DATABASE_PATH)


def cadastrar_usuario(nome, email, senha, confirmar_senha, tipo_usuario="tutor", dados_extras=None):
    """Cadastra um novo usuario"""
    try:
        if not all([nome, email, senha, confirmar_senha]):
            return False, "Preencha todos os campos obrigatorios"

        if senha != confirmar_senha:
            return False, "As senhas nao conferem"

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
            return False, "Este email ja esta cadastrado"

        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo)
            VALUES (?, ?, ?, ?, 1)
        """, (nome, email, senha_hash, data_criacao))

        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Usuario cadastrado: {email} (ID: {usuario_id})")
        return True, "Conta criada com sucesso!"

    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return False, f"Erro ao criar conta: {str(e)}"


def autenticar_usuario(email, senha):
    """Autentica um usuario"""
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
        logger.error(f"Erro na autenticacao: {e}")
        return False, "Erro ao fazer login", None


def buscar_usuario_por_id(usuario_id):
    """Busca usuario por ID"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo
            FROM usuarios 
            WHERE id = ?
        """, (usuario_id,))

        row = cursor.fetchone()

        if row:
            usuario = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'data_criacao': row[3],
                'ativo': bool(row[4]),
                'is_admin': False,
                'tipo_usuario': 'tutor'
            }
            conn.close()
            return usuario

        conn.close()
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuario: {e}")
        return None


def buscar_usuario_por_email(email):
    """Busca usuario por email"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, ativo
            FROM usuarios
            WHERE email = ?
        """, (email.lower().strip(),))

        row = cursor.fetchone()

        if row:
            usuario = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'ativo': bool(row[3])
            }
            conn.close()
            return usuario

        conn.close()
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuario por email: {e}")
        return None


def atualizar_usuario(usuario_id, nome=None, email=None):
    """Atualiza dados do usuario"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Usuario nao encontrado"

        campos = []
        valores = []

        if nome:
            campos.append("nome = ?")
            valores.append(nome.strip().title())

        if email:
            campos.append("email = ?")
            valores.append(email.strip().lower())

        if campos:
            valores.append(usuario_id)
            query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            return True, "Dados atualizados com sucesso!"
        else:
            conn.close()
            return True, "Nenhuma alteracao realizada"

    except Exception as e:
        logger.error(f"Erro ao atualizar usuario: {e}")
        return False, f"Erro ao atualizar dados: {str(e)}"


def alterar_senha(usuario_id, senha_atual, nova_senha, confirmar_nova):
    """Altera a senha do usuario"""
    try:
        if nova_senha != confirmar_nova:
            return False, "As novas senhas nao conferem"

        if len(nova_senha) < 6:
            return False, "A nova senha deve ter pelo menos 6 caracteres"

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT senha_hash FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Usuario nao encontrado"

        senha_hash = row[0]

        if not bcrypt.checkpw(senha_atual.encode('utf-8'), senha_hash):
            conn.close()
            return False, "Senha atual incorreta"

        nova_senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", 
                      (nova_senha_hash, usuario_id))
        conn.commit()
        conn.close()

        return True, "Senha alterada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return False, f"Erro ao alterar senha: {str(e)}"


def deletar_usuario(usuario_id, senha_confirmacao):
    """Desativa um usuario"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT senha_hash FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Usuario nao encontrado"

        senha_hash = row[0]

        if not bcrypt.checkpw(senha_confirmacao.encode('utf-8'), senha_hash):
            conn.close()
            return False, "Senha de confirmacao incorreta"

        cursor.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (usuario_id,))
        conn.commit()
        conn.close()

        return True, "Conta desativada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao desativar usuario: {e}")
        return False, f"Erro ao desativar conta: {str(e)}"
