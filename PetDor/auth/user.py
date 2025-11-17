"""
Gerenciamento de usuários
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
        dados_extras: Dict com dados adicionais

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

        # Formata dados
        nome = nome.strip().title()
        email = email.strip().lower()

        # Hash da senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        # Prepara dados extras
        cnpj = dados_extras.get('cnpj') if dados_extras else None
        endereco = dados_extras.get('endereco') if dados_extras else None
        crmcrmv') if dados_extras else None
        especialidade = dados_extras.get('especialidade') if dados_extras else None

        # Conecta ao banco
        conn = conectar_db()
        cursor = conn.cursor()

        # Verifica se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Este email já está cadastrado"

        # Insere usuário
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Verifica quais colunas existem
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]

        # Monta query baseado nas colunas disponíveis
        campos = ['nome', 'email', 'senha_hash', 'data_criacao', 'ativo']
        valores = [nome, email, senha_hash, data_criacao, 1]

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

        placeholders = ', '.join(['?' for _ in campos])
        campos_str = ', '.join(campos)

        query = f"INSERT INTO usuarios ({campos_str}) VALUES ({placeholders})"
        cursor.execute(query, valores)

        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Usuário cadastrado: {email} (ID: {usuario_id}, Tipo: {tipo_usuario})")

        # Tenta enviar email de confirmação (se módulo existir)
        try:
            from auth.email_confirmation import gerar_token_confirmacao
            from utils.email_sender import enviar_email_confirmacao

            sucesso_token, token = gerar_token_confirmacao(usuario_id, email)
            if sucesso_token:
                enviar_email_confirmacao(email, nome, token)
                return True, f"Conta criada! Verifique seu email ({email}) para confirmar o cadastro."
        except ImportError:
            logger.warning("Módulo de confirmação de email não disponível")

        return True, f"Conta criada com sucesso como {tipo_usuario.title()}!"

    except Exception as e:
        logger.error(f"Erro no cadastro: {e}")
        return False, f"Erro ao criar conta: {e}"


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

        # Monta query baseado nas colunas disponíveis
        campos = ['id', 'nome', 'email', 'data_criacao', 'ativo']

        if 'is_admin' in colunas_existentes:
            campos.append('is_admin')
        if 'tipo_usuario' in colunas_existentes:
            campos.append('tipo_usuario')
        if 'data_desativacao' in colunas_existentes:
            campos.append('data_desativacao')
        if 'motivo_desativacao' in colunas_existentes:
            campos.append('motivo_desativacao')

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
            return False, "Usuário não encontrado"

        # Atualiza campos
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

        if len(nova_senha) < 6:
            return False, "A nova senha deve ter pelo menos 6 caracteres"

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

        # Verifica se colunas de desativação existem
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]

        if 'data_desativacao' in colunas_existentes:
            # Desativa usuário (soft delete)
            data_desativacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE usuarios 
                SET ativo = 0, data_desativacao = ?, motivo_desativacao = ?
                WHERE id = ?
            """, (data_desativacao, "Solicitação do usuário", usuario_id))
        else:
            # Apenas desativa
            cursor.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (usuario_id,))

        conn.commit()
        conn.close()

        logger.info(f"Usuário desativado: {usuario_id}")
        return True, "Conta desativada com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao desativar usuário: {e}")
        return False, f"Erro ao desativar conta: {e}"
