"""
Autenticação e gerenciamento de usuários
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
from utils.validators import validar_nome, validar_email, validar_senha, senhas_conferem

logger = logging.getLogger(__name__)


def conectar_db():
    """Conecta ao banco de dados"""
    from config import DATABASE_PATH
    return sqlite3.connect(DATABASE_PATH)


def criar_usuario(nome, email, senha_hash, tipo_usuario=None):
    """
    Cria um novo usuário no banco

    Args:
        nome: Nome do usuário
        email: Email do usuário
        senha_hash: Hash da senha
        tipo_usuario: Tipo de usuário (clinica, tutor, veterinario)

    Returns:
        Tupla (sucesso, mensagem, usuario_id)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Este e-mail já está cadastrado", None

        # Insere usuário
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, data_criacao, ativo, tipo_usuario)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (nome, email, senha_hash, data_criacao, tipo_usuario))

        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Usuário criado: {email} (ID: {usuario_id}, Tipo: {tipo_usuario or 'padrão'})")
        return True, "Usuário criado com sucesso!", usuario_id

    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        return False, f"Erro ao criar usuário: {e}", None


def cadastrar_usuario(nome, email, senha, confirmar_senha, tipo_usuario=None):
    """
    Cadastra um novo usuário com validações

    Args:
        nome: Nome do usuário
        email: Email do usuário
        senha: Senha do usuário
        confirmar_senha: Confirmação da senha
        tipo_usuario: Tipo de usuário (clinica, tutor, veterinario)

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Validações
        if not nome or not email or not senha or not confirmar_senha:
            return False, "Preencha todos os campos"

        ok_nome, msg_nome = validar_nome(nome)
        if not ok_nome:
            return False, msg_nome

        ok_email, msg_email = validar_email(email)
        if not ok_email:
            return False, msg_email

        ok_senha, msg_senha = validar_senha(senha)
        if not ok_senha:
            return False, msg_senha

        ok_conf, msg_conf = senhas_conferem(senha, confirmar_senha)
        if not ok_conf:
            return False, msg_conf

        # Valida tipo de usuário
        if tipo_usuario not in [None, 'clinica', 'tutor', 'veterinario']:
            return False, "Tipo de usuário inválido"

        # Hash da senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        # Cria usuário
        sucesso, mensagem, usuario_id = criar_usuario(nome, email, senha_hash, tipo_usuario)

        if sucesso:
            logger.info(f"Novo usuário cadastrado: {email} ({tipo_usuario or 'padrão'})")
            return True, f"Conta criada com sucesso! Você foi registrado como {tipo_usuario.title() if tipo_usuario else 'usuário'}."
        else:
            return False, mensagem

    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return False, f"Erro interno no sistema: {e}"


def autenticar_usuario(email, senha):
    """
    Autentica um usuário

    Args:
        email: Email do usuário
        senha: Senha do usuário

    Returns:
        Tupla (sucesso, mensagem, usuario_id)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Busca usuário
        cursor.execute("""
            SELECT id, nome, senha_hash, ativo, tipo_usuario 
            FROM usuarios 
            WHERE email = ? AND ativo = 1
        """, (email,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Email ou senha incorretos", None

        usuario_id, nome, senha_hash, ativo, tipo_usuario = row

        # Verifica senha
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
            conn.close()
            logger.info(f"Usuário autenticado: {email} (ID: {usuario_id})")
            return True, f"Bem-vindo(a), {nome}!", usuario_id
        else:
            conn.close()
            return False, "Email ou senha incorretos", None

    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return False, "Erro na autenticação", None


def buscar_usuario_por_id(usuario_id):
    """
    Busca dados completos de um usuário por ID

    Args:
        usuario_id: ID do usuário

    Returns:
        Dicionário com dados do usuário ou None
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo, is_admin, tipo_usuario,
                   data_desativacao, motivo_desativacao
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
                'is_admin': bool(row[5]),
                'tipo_usuario': row[6],
                'data_desativacao': row[7],
                'motivo_desativacao': row[8]
            }
            conn.close()
            return usuario

        conn.close()
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuário por ID: {e}")
        return None


def buscar_usuario_por_email(email):
    """
    Busca usuário por email

    Args:
        email: Email do usuário

    Returns:
        Dicionário com dados do usuário ou None
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nome, email, ativo, tipo_usuario
            FROM usuarios 
            WHERE email = ?
        """, (email,))

        row = cursor.fetchone()

        if row:
            usuario = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'ativo': bool(row[3]),
                'tipo_usuario': row[4]
            }
            conn.close()
            return usuario

        conn.close()
        return None

    except Exception as e:
        logger.error(f"Erro ao buscar usuário por email: {e}")
        return None


def atualizar_usuario(usuario_id, nome=None, email=None):
    """
    Atualiza dados do usuário

    Args:
        usuario_id: ID do usuário
        nome: Novo nome (None para não alterar)
        email: Novo email (None para não alterar)

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Usuário não encontrado"

        # Atualiza campos
        campos = []
        valores = []

        if nome:
            campos.append("nome = ?")
            valores.append(nome)

        if email:
            campos.append("email = ?")
            valores.append(email)

        if campos:
            valores.append(usuario_id)
            query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()

            logger.info(f"Usuário atualizado: ID {usuario_id}")
            conn.close()
            return True, "Dados atualizados com sucesso!"
        else:
            conn.close()
            return True, "Nenhuma alteração realizada"

    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
        return False, f"Erro ao atualizar dados: {e}"


def alterar_senha(usuario_id, senha_atual, nova_senha, confirmar_nova):
    """
    Altera a senha do usuário

    Args:
        usuario_id: ID do usuário
        senha_atual: Senha atual
        nova_senha: Nova senha
        confirmar_nova: Confirmação da nova senha

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Validações
        if nova_senha != confirmar_nova:
            return False, "As novas senhas não conferem"

        ok_senha, msg_senha = validar_senha(nova_senha)
        if not ok_senha:
            return False, msg_senha

        # Verifica senha atual
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT senha_hash FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Usuário não encontrado"

        senha_hash = row[0]

        if not bcrypt.checkpw(senha_atual.encode('utf-8'), senha_hash):
            conn.close()
            return False, "Senha atual incorreta"

        # Hash da nova senha
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())

        # Atualiza senha
        cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", 
                      (nova_senha_hash, usuario_id))
        conn.commit()
        conn.close()

        logger.info(f"Senha alterada para usuário: {usuario_id}")
        return True, "Senha alterada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return False, f"Erro ao alterar senha: {e}"


def deletar_usuario(usuario_id, senha_confirmacao):
    """
    Desativa (soft delete) um usuário

    Args:
        usuario_id: ID do usuário
        senha_confirmacao: Senha para confirmação

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica senha
        cursor.execute("SELECT senha_hash FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Usuário não encontrado"

        senha_hash = row[0]

        if not bcrypt.checkpw(senha_confirmacao.encode('utf-8'), senha_hash):
            conn.close()
            return False, "Senha de confirmação incorreta"

        # Desativa usuário (soft delete)
        data_desativacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE usuarios 
            SET ativo = 0, data_desativacao = ?, motivo_desativacao = ?
            WHERE id = ?
        """, (data_desativacao, "Solicitação do usuário", usuario_id))

        conn.commit()
        conn.close()

        logger.info(f"Usuário desativado: {usuario_id}")
        return True, "Conta desativada com sucesso! Você pode reativá-la posteriormente."

    except Exception as e:
        logger.error(f"Erro ao desativar usuário: {e}")
        return False, f"Erro ao desativar conta: {e}"


def listar_usuarios(tipo_filtro=None, ativo=True):
    """
    Lista todos os usuários com filtros opcionais

    Args:
        tipo_filtro: Filtrar por tipo (clinica, tutor, veterinario)
        ativo: Filtrar por status ativo (True/False/None para todos)

    Returns:
        Lista de dicionários com dados dos usuários
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        query = """
            SELECT id, nome, email, data_criacao, ativo, is_admin, tipo_usuario,
                   data_desativacao, motivo_desativacao
            FROM usuarios
        """
        params = []

        condicoes = []
        if tipo_filtro:
            condes.append("tipo_usuario = ?")
            params.append(tipo_filtro)

        if ativo is not None:
            condicoes.append("ativo = ?")
            params.append(1 if ativo else 0)

        if condicoes:
            query += " WHERE " + " AND ".join(condicoes)

        query += " ORDER BY data_criacao DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        usuarios = []
        for row in rows:
            usuario = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'data_criacao': row[3],
                'ativo': bool(row[4]),
                'is_admin': bool(row[5]),
                'tipo_usuario': row[6],
                'data_desativacao': row[7],
                'motivo_desativacao': row[8]
            }
            usuarios.append(usuario)

        conn.close()
        return usuarios

    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return []


def ativar_usuario(usuario_id):
    """
    Reativa um usuário desativado

    Args:
        usuario_id: ID do usuário

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se usuário existe e está desativado
        cursor.execute("""
            SELECT id FROM usuarios 
            WHERE id = ? AND ativo = 0
        """, (usuario_id,))

        if not cursor.fetchone():
            conn.close()
            return False, "Usuário não encontrado ou já está ativo"

        # Reativa usuário
        cursor.execute("""
            UPDATE usuarios 
            SET ativo = 1, data_desativacao = NULL, motivo_desativacao = NULL
            WHERE id = ?
       ", (usuario_id,))

        conn.commit()
        conn.close()

        logger.info(f"Usuário reativado: {usuario_id}")
        return True, "Usuário reativado com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao reativar usuário: {e}")
        return False, f"Erro ao reativar usuário: {e}"


def definir_admin(usuario_id, is_admin=True):
    """
    Define ou remove status de admin

    Args:
        usuario_id: ID do usuário
        is_admin: True para admin, False para remover

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Usuário não encontrado"

        cursor.execute("UPDATE usuarios SET is_admin = ? WHERE id = ?", 
                      (1 if is_admin else 0, usuario_id))

        conn.commit()
        conn.close()

        status = "admin" if is_admin else "usuário comum"
        logger.info(f"Usuário {usuario_id} definido como {status}")
        return True, f"Usuário definido como {status} com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao definir admin: {e}")
        return False, f"Erro ao alterar permissão: {e}"
