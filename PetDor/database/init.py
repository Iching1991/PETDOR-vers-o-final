"""
Inicialização do pacote database do PETDOR.

Expõe apenas o módulo migration, 
pois connection.py não está mais dentro da pasta.
"""

from .migration import criar_tabelas

__all__ = ["criar_tabelas"]
