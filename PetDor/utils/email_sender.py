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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def enviar_email_reset(email_destino, token):
    """
    Envia email de reset de senha

    Args:
        email_destino: Email do destinatário
        token: Token de reset

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Modo demo - não envia email real
        logger.info(f"[DEMO] Email de reset solicitado para: {email_destino}")
        logger.info(f"[DEMO] Token gerado: {token}")
        logger.info(f"[DEMO] Link: https://petdor.streamlit.app/reset_senha?token={token}")

        # Em produção, você configuraria SMTP aqui
        # Exemplo com Gmail:
        # smtp_server = "smtp.gmail.com"
        # smtp_port = 587
        # email_remetente = "seu_email@gmail.com"
        # senha_email = "sua_senha_app"

        # msg = MIMEMultipart()
        # msg['From'] = f"PETDor <{email_remetente}>"
        # msg['To'] = email_destino
        # msg['Subject'] = "PETDor - Recuperação de Senha"

        # corpo = f"""
        # Olá!
        # 
        # Você solicitou a recuperação de senha da sua conta PETDor.
        # 
        # Para redefinir sua senha, clique no link abaixo:
        # https://petdor.streamlit.app/reset_senha?token={token}
        # 
        # ⚠️ Este link expira em 1 hora por questões de segurança.
        # 
        # Se você não solicitou esta recuperação, ignore este email.
        # 
        # Atenciosamente,
        # Equipe PETDor
        # """

        # msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(email_remetente, senha_email)
        # text = msg.as_string()
        # server.sendmail(email_remetente, email_destino, text)
        # server.quit()

        return True, "Email enviado com sucesso (modo demo)"

    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        return False, f"Erro ao enviar email: {str(e)}"
