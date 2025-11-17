import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent

# Caminho do banco de dados
# Usa variável de ambiente para permitir flexibilização
DATABASE_PATH = os.getenv("DATABASE_PATH", "C:/Databases/petdor.db")

# Configurações do app
APP_CONFIG = {
    'titulo': 'PETDOR',
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
