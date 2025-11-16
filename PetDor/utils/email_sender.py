"""
Envio de emails para recuperação de senha
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging
from config import EMAIL_CONFIG

logger = logging.getLogger(__name__)

def enviar_email_reset(email_destino, token):
    """Envia email de reset de senha"""
    try:
        if not EMAIL_CONFIG:
            logger.warning("Configuração de email não encontrada - modo demo ativado")
            return True, "Email enviado (modo demo)"

        # Configuração do email
        smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
        smtp_port = EMAIL_CONFIG.get('smtp_port', 587)
        email_remetente = EMAIL_CONFIG.get('email_remetente')
        senha_email = EMAIL_CONFIG.get('senha_email')

        if not all([email_remetente, senha_email]):
            logger.warning("Credenciais de email incompletas - modo demo ativado")
            return True, "Email enviado (modo demo)"

        # Cria mensagem
        msg = MimeMultipart()
        msg['From'] = f"PETDor <{email_remetente}>"
        msg['To'] = email_destino
        msg['Subject'] = "PETDor - Recuperação de Senha"

        # Corpo do email
        corpo = f"""
        Olá!

        Você solicitou a recuperação de senha da sua conta PETDor.

        Para redefinir sua senha, clique no link abaixo:
        https://petdor.streamlit.app/?token={token}

        ⚠️ Este link expira em 1 hora por questões de segurança.

        Se você não solicitou esta recuperação, ignore este email.

        Atenciosamente,
        Equipe PETDor
        """

        msg.attach(MimeText(corpo, 'plain', 'utf-8'))

        # Envia email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_remetente, senha_email)
        text = msg.as_string()
        server.sendmail(email_remetente, email_destino, text)
        server.quit()

        logger.info(f"Email de reset enviado para: {email_destino}")
        return True, "Email enviado com sucesso"

    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        return False, f"Erro ao enviar email: {str(e)}"
