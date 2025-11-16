"""
Páginas principais da interface PETDor.

Cada módulo contém uma função `render()` que desenha a página no Streamlit.
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
