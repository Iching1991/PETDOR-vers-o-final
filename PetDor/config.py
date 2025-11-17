import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent

# Caminho único e fixo do banco de dados
DATABASE_PATH = ROOT_DIR / "database" / "petdor.db"

# Configurações do app
APP_CONFIG = {
    'titulo': 'PETDOR',
    'versao': '1.0.0',
    'autor': 'Salute Vitae AI'
}

EMAIL_CONFIG = {
    'smtp_server': 'smtpout.secureserver.net',
    'smtp_port': 587,
    'remetente': 'relatorio@petdor.app',
    'usuario': os.getenv('EMAIL_USER', 'relatorio@petdor.app'),
    'senha': os.getenv('EMAIL_PASSWORD', '')
}

}


