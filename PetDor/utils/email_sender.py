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

    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")
        return False


# -----------------------------------------------------------
# HTML PARA E-MAIL DE BOAS-VINDAS
# -----------------------------------------------------------

def gerar_html_boas_vindas(nome: str) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f7fa; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px;
                    padding: 20px; border: 1px solid #e5e9f0;">
          <h2 style="color: #2b8aef;">🐾 Bem-vindo ao PET DOR</h2>
          <p>Olá <strong>{nome}</strong>,</p>
          <p>Seu cadastro foi concluído com sucesso.</p>

          <p style="text-align: center; margin: 25px 0;">
            <a href="{APP_URL}"
               style="background:#2b8aef; padding: 12px 24px; color:#fff; text-decoration:none; border-radius:6px;">
              Acessar PET DOR
            </a>
          </p>

          <p>Atenciosamente,<br>Equipe PET DOR 🐾</p>
        </div>
      </body>
    </html>
    """


# -----------------------------------------------------------
# HTML PARA RESET DE SENHA (FUNÇÃO FALTANDO)
# -----------------------------------------------------------

def gerar_html_reset_senha(nome: str, link_reset: str) -> str:
    """
    Retorna o HTML do e-mail de redefinição de senha.
    """
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f7fa; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px;
                    padding: 20px; border: 1px solid #e5e9f0;">
          <h2 style="color: #e63946;">🔐 Recuperação de Senha</h2>

          <p>Olá <strong>{nome}</strong>,</p>

          <p>Recebemos uma solicitação para redefinir sua senha.</p>

          <p style="text-align:center; margin: 25px 0;">
            <a href="{link_reset}"
               style="background:#e63946; padding: 12px 24px; color:#fff; text-decoration:none; border-radius:6px;">
              Redefinir Senha
            </a>
          </p>

          <p>Este link expira em {TOKEN_EXP_HOURS} horas.</p>

          <p>Se não foi você, apenas ignore este e-mail.</p>

          <p>Atenciosamente,<br>Equipe PET DOR 🐾</p>
        </div>
      </body>
    </html>
    """

