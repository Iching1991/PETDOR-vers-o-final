"""
Módulo utilitário do PETDor.

Contém funções auxiliares como:
- validações,
- envio de e-mails,
- geração de PDFs.
"""

# utils/__init__.py

from . import email_sender
from . import pdf_generator
from . import validator

__all__ = [
    "validators",
    "email_sender",
    "pdf_generator",
]


