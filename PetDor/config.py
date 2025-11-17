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

def get_nivel_dor(percentual):
    """
    Retorna o nível de dor baseado no percentual

    Args:
        percentual: Percentual de dor (0-100)

    Returns:
        Dicionário com nível e texto de recomendação
    """
    if percentual < 30:
        return {
            "nivel": "Baixo",
            "cor": "#28a745",
            "texto": "Monitoramento de rotina. Sem sinais significativos de dor."
        }
    elif percentual < 60:
        return {
            "nivel": "Moderado",
            "cor": "#ffc107",
            "texto": "Atenção necessária. Considere intervenção veterinária."
        }
    else:
        return {
            "nivel": "Alto",
            "cor": "#dc3545",
            "texto": "Intervenção urgente recomendada. Consulte veterinário imediatamente."
        }

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

