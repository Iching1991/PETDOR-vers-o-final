"""
Pacote database do PETDOR.
Inicializa e migra o banco.
"""

from .connection import conectar_db
from .migration import migrar_banco_completo

__all__ = ["conectar_db", "migrar_banco_completo"]
