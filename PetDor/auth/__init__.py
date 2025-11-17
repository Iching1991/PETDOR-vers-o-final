"""
Módulo de autenticação do PETDor
Gerencia cadastro, login, recuperação de senha e confirmação de email
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Importa apenas o que existe e está funcionando
try:
    from .user import (
        cadastrar_usuario,
        autenticar_usuario,
        buscar_usuario_por_id,
        buscar_usuario_por_email,
        atualizar_usuario,
        alterar_senha,
        deletar_usuario
    )
except ImportError as e:
    print(f"Erro ao importar user: {e}")
    # Define funções vazias para evitar erro total
    def cadastrar_usuario(*args, **kwargs):
        return False, "Módulo user não disponível"
    def autenticar_usuario(*args, **kwargs):
        return False, "Módulo user não disponível", None
    def buscar_usuario_por_id(*args, **kwargs):
        return None
    def buscar_usuario_por_email(*args, **kwargs):
        return None
    def atualizar_usuario(*args, **kwargs):
        return False, "Módulo user não disponível"
    def alterar_senha(*args, **kwargs):
        return False, "Módulo user não disponível"
    def deletar_usuario(*args, **kwargs):
        return False, "Módulo user não disponível"

try:
    from .password_reset import (
        criar_token_reset,
        validar_token_reset,
        redefinir_senha,
        marcar_token_usado
    )
except ImportError as e:
    print(f"Erro ao importar password_reset: {e}")
    def criar_token_reset(*args, **kwargs):
        return False, None
    def validar_token_reset(*args, **kwargs):
        return False, None, "Módulo não disponível"
    def redefinir_senha(*args, **kwargs):
        return False, "Módulo não disponível"
    def marcar_token_usado(*args, **kwargs):
        return False

try:
    from .email_confirmation import (
        gerar_token_confirmacao,
        validar_token_confirmacao,
        confirmar_email,
        reenviar_email_confirmacao,
        buscar_usuario_por_token,
        verificar_email_confirmado
    )
except ImportError as e:
    print(f"Aviso: email_confirmation não disponível: {e}")
    # Funções placeholder
    def gerar_token_confirmacao(*args, **kwargs):
        return True, "dummy_token"
    def validar_token_confirmacao(*args, **kwargs):
        return True, 1, "Token válido"
    def confirmar_email(*args, **kwargs):
        return True, "Email confirmado"
    def reenviar_email_confirmacao(*args, **kwargs):
        return False, "Módulo não disponível", None, None
    def buscar_usuario_por_token(*args, **kwargs):
        return None
    def verificar_email_confirmado(*args, **kwargs):
        return True

__all__ = [
    'cadastrar_usuario',
    'autenticar_usuario',
    'buscar_usuario_por_id',
    'buscar_usuario_por_email',
    'atualizar_usuario',
    'alterar_senha',
    'deletar_usuario',
    'criar_token_reset',
    'validar_token_reset',
    'redefinir_senha',
    'marcar_token_usado',
    'gerar_token_confirmacao',
    'validar_token_confirmacao',
    'confirmar_email',
    'reenviar_email_confirmacao',
    'buscar_usuario_por_token',
    'verificar_email_confirmado'
]
