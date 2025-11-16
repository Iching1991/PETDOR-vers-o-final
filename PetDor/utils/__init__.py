"""
Módulo de utilitários do PETDor.

Responsável por:
- validação de dados,
- envio de emails,
- geração de PDFs,
- funções auxiliares.
"""

from . import validators
from . import email_sender

__all__ = [
    "validators",
    "email_sender",
]
