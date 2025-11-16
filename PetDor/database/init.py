"""
Módulo de gerenciamento de banco de dados do PETDor.

Responsável por:
- conexão com SQLite,
- inicialização de tabelas,
- operações CRUD de usuários e avaliações.
"""

__all__ = [
    "connection",
    "models",
]
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

