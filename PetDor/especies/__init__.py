"""
Módulo relacionado às espécies atendidas no PETDor.

Contém:
- classes base,
- dados de cães e gatos,
- carregador central.
"""

from . import base
from . import caes
from . import gatos
from . import loader

__all__ = [
    "base",
    "caes",
    "gatos",
    "loader",
]
