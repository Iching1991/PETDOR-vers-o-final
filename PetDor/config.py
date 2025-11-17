import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent

# Banco de dados
# Você pode usar variável de ambiente para mudar facilmente o local do banco sem alterar o código
DATABASE_PATH = os.getenv("DATABASE_PATH", "C:/Databases/petdor.db") 

# Configurações do app
APP_CONFIG = {
    'titulo': 'PETDor',
    'versao': '1.0.0',
    'autor': 'Salute Vitae AI'
}

# Configurações de email (GoDaddy)
EMAIL_CONFIG = {
    'smtp_server': 'smtpout.secureserver.net',
    'smtp_port': 587,
    'remetente': 'contato@petdor.app',
    'usuario': os.getenv('EMAIL_USER', 'contato@petdor.app'),
    'senha': os.getenv('EMAIL_PASSWORD', '')
}


