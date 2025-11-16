"""
Módulo de banco de dados do PETDor.

Inclui:
- inicialização do banco,
- criação de conexões,
- modelos de dados.
"""

from . import connection
from . import init
from . import models

__all__ = [
    "connection",
    "init",
    "models",
]
