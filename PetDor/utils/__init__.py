"""
Módulo utilitário do PETDor.

Contém funções auxiliares como:
- validações,
- envio de e-mails,
- geração de PDFs.
"""

from . import email_sender
from . import pdf_generator
from . import validator

__all__ = [
    "validator",
    "email_sender",
    "pdf_generator",
]
