"""
Módulo de perguntas por espécie do PETDor

Contém perguntas específicas para avaliação de dor por espécie:
- base: classes base para perguntas e configurações
- Cão: perguntas para cães
- Gato: perguntas para gatos
"""

from . import base, cao, gato

__all__ = ["base", "cao", "gato"]
