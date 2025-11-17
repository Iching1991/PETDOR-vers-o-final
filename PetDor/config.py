"""
Configuracoes do PETDor
"""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Diretorio raiz do projeto
ROOT_DIR = Path(__file__).parent

# Banco de dados
DATABASE_PATH = ROOT_DIR / "petdor.db"

# Configuracoes do app
APP_CONFIG = {
    'titulo': 'PETDor',
    'versao': '1.0.0',
    'autor': 'Agnaldo Angelico Baldissera'
}

# Configuracoes de email
EMAIL_CONFIG = {
    'smtp_server': 'smtpout.secureserver.net',
    'smtp_port': 587,
    'remetente': os.getenv('EMAIL_USER', 'contato@petdor.app'),
    'usuario': os.getenv('EMAIL_USER', 'contato@petdor.app'),
    'senha': os.getenv('EMAIL_PASSWORD', '')
}
