"""
Módulo de autenticação do PETDor

Contém funcionalidades de:
- Cadastro e autenticação de usuários
- Recuperação de senha
- Confirmação de email
- Gerenciamento de contas
"""
from .user import (
    cadastrar_usuario,
    autenticar_usuario,
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    atualizar_usuario,
    alterar_senha,
    deletar_usuario,
    listar_usuarios,
    ativar_usuario,
    definir_admin
)

from .password_reset import (
    criar_token_reset,
    validar_token_reset,
    redefinir_senha,
    marcar_token_usado,
    buscar_usuario_por_email as buscar_email_reset
)

from .email_confirmation import (
    gerar_token_confirmacao,
    validar_token_confirmacao,
    confirmar_email,
    reenviar_email_confirmacao,
    buscar_usuario_por_token,
    verificar_email_confirmado
)

__all__ = [
    # Gerenciamento de usuários
    'cadastrar_usuario',
    'autenticar_usuario',
    'buscar_usuario_por_id',
    'buscar_usuario_por_email',
    'atualizar_usuario',
    'alterar_senha',
    'deletar_usuario',
    'listar_usuarios',
    'ativar_usuario',
    'definir_admin',

    # Recuperação de senha
    'criar_token_reset',
    'validar_token_reset',
    'redefinir_senha',
    'marcar_token_usado',

    # Confirmação de email
    'gerar_token_confirmacao',
    'validar_token_confirmacao',
    'confirmar_email',
    'reenviar_email_confirmacao',
    'buscar_usuario_por_token',
    'verificar_email_confirmado'
]
