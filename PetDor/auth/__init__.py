# auth/__init__.py

"""
Módulo de autenticação do PETDor.

Responsável por:
- gerenciamento de usuários,
- autenticação,
- fluxo de recuperação e redefinição de senha.
"""

# Não importe os submódulos aqui para evitar importação circular
# Os arquivos que precisarem devem importar diretamente:
# from auth.user import cadastrar_usuario
# from auth.password_reset import solicitar_reset

__all__ = [
    "user",
    "password_reset",
]
