"""
Módulo de inicialização do pacote database do PETDOR.

Expõe módulos para importação.
"""

from .connection import conectar_db
from .migration import criar_tabelas

__all__ = ["conectar_db", "criar_tabelas"]
