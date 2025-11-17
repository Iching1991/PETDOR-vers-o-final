"""
Gerenciamento de usuários do PETDor
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
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


def conectar_db():
    """Conecta ao banco de dados"""
    return sqlite3.connect(DATABASE_PATH)


def cadastrar_usuario(nome, email, senha, confirmar_senha, tipo_usuario="tutor", dados_extras=None):
    """
    Cadastra um novo usuário

    Args:
        nome: Nome do usuário
        email: Email do usuário
        senha: Senha do usuário
        confirmar_senha: Confirmação da senha
        tipo_usuario: Tipo (tutor, clinica, veterinario)
        dados_extras: Dict com dados adicionais (cnpj, endereco, crmv, especialidade)

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Validações básicas
        if not all([nome, email, senha, confirmar_senha]):
            return False, "Preencha todos os campos obrigatórios"

        if senha != confirmar_senha:
            return False, "As senhas não conferem"

        if len(senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres"

        # Formata dados (Title Case para nome, minúsculo para email)
        nome = nome.strip().title()
        email = email.strip().lower()

        # Valida tipo de usuário
        tipos_validos = ['tutor', 'clinica', 'veterinario']
        if tipo_usuario not in tipos_validos:
            return False, "Tipo de usuário inválido"

        # Hash da senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        # Prepara dados extras
        if dados_extras is None:
            dados_extras = {}

        cnpj = dados_extras.get('cnpj')
        endereco = dados_extras.get('endereco')
        crmv = dados_extras.get('crmv')
        especialidade = dados_extras.get('especialidade')

        # Conecta ao banco
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Este email já está cadastrado"

        # Verifica quais colunas existem na tabela
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]

        # Monta query dinamicamente baseado nas colunas disponíveis
        campos = ['nome', 'email', 'senha_hash', 'data_criacao', 'ativo']
        valores = [nome, email, senha_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1]

        if 'tipo_usuario' in colunas_existentes:
            campos.append('tipo_usuario')
            valores.append(tipo_usuario)

        if 'cnpj' in colunas_existentes and cnpj:
            campos.append('cnpj')
            valores.append(cnpj)

        if 'endereco' in colunas_existentes and endereco:
            campos.append('endereco')
            valores.append(endereco)

        if 'crmv' in colunas_existentes and crmv:
            campos.append('crmv')
            valores.append(crmv)

        if 'especialidade' in colunas_existentes and especialidade:
            campos.append('especialidade')
            valores.append(especialidade)

        if 'email_confirmado' in colunas_existentes:
            campos.append('email_confirmado')
            valores.append(0)

        # Monta e executa query
        placeholders = ', '.join(['?' for _ in campos])
        campos_str = ', '.join(campos)
        query = f"INSERT INTO usuarios ({campos_str}) VALUES ({placeholders})"

        cursor.execute(query, valores)
        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Usuário cadastrado: {email} (ID: {usuario_id}, Tipo: {tipo_usuario})")

        # Tenta enviar email de confirmação
        try:
            from auth.email_confirmation import gerar_token_confirmacao
            from utils.email_sender import enviar_email_confirmacao

            sucesso_token, token = gerar_token_confirmacao(usuario_id, email)
            if sucesso_token:
                sucesso_email, msg_email = enviar_email_confirmacao(email, nome, token)
                if sucesso_email:
                    return True, f"Conta criada! Verifique seu email ({email}) para confirmar o cadastro."
                else:
                    logger.warning(f"Email não enviado: {msg_email}")
        except ImportError as e:
            logger.warning(f"Módulo de confirmação não disponível: {e}")
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")

        return True, f"Conta criada com sucesso como {tipo_usuario.title()}!"

    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return False, f"Erro ao criar conta: {str(e)}"


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
            SELECT id, nome, senha_hash, ativo 
            FROM usuarios 
            WHERE email = ?
        """, (email.lower().strip(),))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Email ou senha incorretos", None

        usuario_id, nome, senha_hash, ativo = row

        # Verifica se está ativo
        if not ativo:
            conn.close()
            return False, "Conta desativada. Entre em contato com o suporte.", None

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
        return False, "Erro ao fazer login", None


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

        # Verifica quais colunas existem
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]

        # Campos básicos sempre presentes
        campos = ['id', 'nome', 'email', 'data_criacao', 'ativo']

        # Adiciona campos opcionais se existirem
        campos_opcionais = ['is_admin', 'tipo_usuario', 'data_desativacao', 'motivo_desativacao', 
                           'cnpj', 'endereco', 'crmv', 'especialidade', 'email_confirmado']

        for campo in campos_opcionais:
            if campo in colunas_existentes:
                campos.append(campo)

        campos_str = ', '.join(campos)
        cursor.execute(f"SELECT {campos_str} FROM usuarios WHERE id = ?", (usuario_id,))

        row = cursor.fetchone()

        if row:
            usuario = {}
            for i, campo in enumerate(campos):
                usuario[campo] = row[i]

            # Valores padrão para campos opcionais
            if 'is_admin' not in usuario:
                usuario['is_admin'] = False
            if 'tipo_usuario' not in usuario:
                usuario['tipo_usuario'] = 'tutor'
            if 'email_confirmado' not in usuario:
                usuario['email_confirmado'] = True

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
            return False
