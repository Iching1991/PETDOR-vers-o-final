"""
Envio de e-mails em HTML (boas-vindas e reset de senha)
"""
import smtplib
import ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SMTP_CONFIG, APP_URL, TOKEN_EXP_HOURS

logger = logging.getLogger(__name__)


def enviar_email_html(destinatario: str, assunto: str, html_body: str) -> bool:
    """
    Envia um e-mail com corpo HTML.
    Retorna True se enviado com sucesso.
    """
    try:
        if not SMTP_CONFIG.get("user") or not SMTP_CONFIG.get("password"):
            logger.error("Configuração SMTP incompleta.")
            return False

        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_CONFIG["user"]
        msg["To"] = destinatario
        msg["Subject"] = assunto

        part = MIMEText(html_body, "html", "utf-8")
        msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            SMTP_CONFIG["server"],
            SMTP_CONFIG["port"],
            context=context,
        ) as server:
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.sendmail(SMTP_CONFIG["user"], destinatario, msg.as_string())

        logger.info(f"E-mail enviado para {destinatario}: {assunto}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Erro de autenticação SMTP. Verifique usuário/senha.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"Erro SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar e-mail: {e}")
        return False


def gerar_html_boas_vindas(nome: str) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f7fafc; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px;
                    padding: 20px; border: 1px solid #e2e8f0;">
          <h2 style="color: #2b8aef;">🐾 Bem-vindo ao PET DOR</h2>
          <p>Olá <strong>{nome}</strong>,</p>
          <p>
            Seu cadastro foi realizado com sucesso. Agora você pode utilizar o PET DOR
            para avaliar a dor dos seus pacientes ou pets de forma organizada.
          </p>
          <p>Clique no botão abaixo para acessar o sistema:</p>
          <p style="text-align: center; margin: 20px 0;">
            <a href="{APP_URL}" 
               style="background-color: #2b8aef; color: #ffffff; padding: 10px 20px; 
                      border-radius: 6px; text-decoration: none; font-weight: bold;">
              Acessar PET DOR
            </a>
          </p>
          <p style="


