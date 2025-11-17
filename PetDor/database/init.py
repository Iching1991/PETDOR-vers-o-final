"""
Módulo de inicialização do pacote database do PETDOR.

Expõe os módulos connection, migration e models para fácil acesso.
"""

from . import connection
from . import migration

connection.conectar_db()
migration.criar_tabelas()

__all__ = ["connection", "migration", "models"]
