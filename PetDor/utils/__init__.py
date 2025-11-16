"""
Módulo utilitário do PETDor.

Contém funções auxiliares como:
- validações,
- envio de e-mails,
- geração de PDFs.
"""

from.import validators
from.import email_sender
from.import pdf_generator

__all__ = [
    "validators",
    "email_sender",
    "pdf_generator",
]

