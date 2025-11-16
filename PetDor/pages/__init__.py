"""
Módulo de páginas do PETDor.

Responsável por:
- interface de cadastro e login,
- avaliação de dor,
- histórico de avaliações,
- gerenciamento de conta,
- recuperação de senha.
"""

from . import avaliacao
from . import cadastro
from . import conta
from . import historico
from . import login
from . import recuperar_senha
from . import reset_senha

__all__ = [
    "avaliacao",
    "cadastro",
    "conta",
    "historico",
    "login",
    "recuperar_senha",
    "reset_senha",
]


