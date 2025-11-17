"""
Módulo de utilitários do PETDor.

Responsável por:
- validação de dados,
- envio de emails,
- geração de PDFs,
- funções auxiliares.
"""

# Não importe os submódulos aqui para evitar conflitos
# Os arquivos que precisarem devem importar diretamente:
# from utils.validators import validar_email
# from utils.email_sender import enviar_email_reset
# from utils.pdf_generator import gerar_relatorio_pdf

__all__ = [
    "validators",
    "email_sender",
    "pdf_generator",
]
