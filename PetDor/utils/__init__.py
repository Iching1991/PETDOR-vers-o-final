"""
Módulo utilitário do PETDor

Este pacote contém funções auxiliares usadas em todo o sistema,
como validações, envio de e-mails e geração de PDFs.
"""

# Exposição organizada dos módulos do pacote utils
from . import validators
from . import email_sender
from . import pdf_generator

__all__ = [
    "validators",
    "email_sender",
    "pdf_generator",
]
