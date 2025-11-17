"""
Módulo de banco de dados do PETDor.

Responsável por:
- conexão com SQLite,
- inicialização de tabelas,
- migrações,
- modelos de dados.
"""

from . import connection
from . import migration
from . import models

__all__ = [
    "connection",
    "migration",
    "models",
]
