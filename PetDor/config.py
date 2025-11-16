"""
Configurações do PETDor
"""
import os
from pathlib import Path

# Caminho do banco de dados
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "petdor.db"

# Configuração de email (opcional - para produção)
EMAIL_CONFIG = {
    # 'smtp_server': 'smtp.gmail.com',
    # 'smtp_port': 587,
    # 'email_remetente': 'seu_email@gmail.com',
    # 'senha_email': 'sua_senha_app',
}

# Configurações do app
APP_CONFIG = {
    'titulo': 'PETDor - Avaliação de Dor em Pets',
    'versao': '1.0.0',
    'descricao': 'Aplicativo para avaliação de dor em cães e gatos',
    'autor': 'PETDor Team',
}

# Configurações de segurança
SECURITY_CONFIG = {
    'senha_min_length': 6,
    'token_expiry_hours': 1,
    'max_login_attempts': 5,
}
