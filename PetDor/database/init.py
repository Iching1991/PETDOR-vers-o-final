"""
Inicialização do pacote database do PETDOR.
Expõe funções centrais de conexão e migração.
"""

from .connection import conectar_db
from .migration import migrar_banco_completo

__all__ = ["conectar_db", "migrar_banco_completo"]
