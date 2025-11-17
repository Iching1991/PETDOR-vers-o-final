"""
Módulo de gerenciamento de banco de dados do PETDor.

Responsável por:
- Conexão com SQLite
- Inicialização de tabelas
- Migrações de schema
- Modelos de dados
"""

from . import connection
from . import migration
from . import models

__all__ = [
    "connection",
    "migration",
    "models",
]
