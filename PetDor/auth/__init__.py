"""
Módulo de autenticação do PETDor.

Responsável por:
- gerenciamento de usuários,
- autenticação,
- fluxo de recuperação e redefinição de senha.
"""

from . import user
from . import password_reset

__all__ = [
    "user",
    "password_reset",
]
