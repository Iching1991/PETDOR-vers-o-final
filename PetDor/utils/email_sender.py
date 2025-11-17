"""
Envio de emails para recuperação de senha (SMTP genérico, ex: GoDaddy)
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
import os

logger = logging.getLogger(__name__)


def enviar_email_reset(email_destino: str, token: str):
    """
    Envia email de reset de senha para o usuário.

    Usa configurações de SMTP vindas de:
    - st.secrets (no Streamlit Cloud), ou
    - variáveis de ambiente (localmente).
    """
    try:
        # Tenta ler do Streamlit secrets (Cloud)
        try:
            import streamlit as st
            smtp_server = st.secrets.get("SMTP_SERVER", "")
            smtp_port = int(st.secrets.get("SMTP_PORT", "587"))
            email_remetente = st.secrets.get("EMAIL_REMETENTE", "")
            senha_email = st.secrets.get("SENHA_EMAIL", "")
        except Exception:
            # Fallback: tenta variáveis de ambiente (local)
            smtp_server = os.getenv("SMTP_SERVER", "")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            email_remetente = os.getenv("EMAIL_REMETENTE", "")
            senha_email = os.getenv("SENHA_EMAIL", "")

        # Verificações básicas
        if not smtp_server or not email_remetente or not senha_email:
            logger.warning("Configuração de SMTP incompleta. Usando modo demo.")
            logger.info(f"[DEMO] Enviaria email para: {email_destino}")
            logger.info(f"[DEMO] Token: {token}")
            logger.info(
                f"[DEMO] Link: https://petdor.streamlit.app/reset_senha?token={token}"
            )
            return True, "Email enviado (modo demo - SMTP não configurado)."

        # Monta a mensagem
        msg = MIMEMultipart("alternative")
        msg["From"] = f"PETDor <{email_remetente}>"
        msg["To"] = email_destino
        msg["Subject"] = "PETDor - Recuperação de Senha"

        link = f"https://petdor.streamlit.app/reset_senha?token={token}"

        texto_simples = f"""Olá!

Você solicitou a recuperação de senha da sua conta PETDor.

Para redefinir sua senha, acesse o link:
{link}

⚠️ Este link expira em 1 hora por questões de segurança.

Se você não solicitou esta recuperação, ignore este email.

Atenciosamente,
Equipe PETDor
"""

        texto_html = f"""
<html>
  <head>
    <style>
      body {{
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
      }}
      .container {{
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 10px;
      }}
      .header {{
        background: linear-gradient(135deg, #AEE3FF, #C7F9CC);
        padding: 20px;
        text-align: center;
        border-radius: 10px 10px 0 0;
      }}
      .content {{
        background: white;
        padding: 30px;
        border-radius: 0 0 10px 10px;
      }}
      .button {{
        display: inline-block;
        padding: 15px 30px;
        background-color: #28a745;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin: 20px 0;
        font-weight: bold;
      }}
      .warning {{
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 20px 0;
      }}
      .footer {{
        text-align: center;
        color: #666;
        font-size: 12px;
        margin-top: 20px;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1 style="margin: 0; color: #2d3748;">🐾 PETDor</h1>
        <p style="margin: 5px 0; color: #4a5568;">Recuperação de Senha</p>
      </div>
      <div class="content">
        <p>Olá!</p>
        <p>Você solicitou a recuperação de senha da sua conta PETDor.</p>
        <p>Para redefinir sua senha, clique no botão abaixo:</p>
        <div style="text-align: center;">
          <a href="{link}" class="button">
            Redefinir Senha
          </a>
        </div>
        <div class="warning">
          <strong>⚠️ Atenção:</strong> Este link expira em 1 hora por questões de segurança.
        </div>
        <p>Se você não solicitou esta recuperação, ignore este email.</p>
        <p>Atenciosamente,<br><strong>Equipe PETDor</strong></p>
      </div>
      <div class="footer">
        <p>Este é um email automático, por favor não responda.</p>
        <p>&copy; 2024 PETDor - Todos os direitos reservados</p>
      </div>
    </div>
  </body>
</html>
"""

        parte_texto = MIMEText(texto_simples, "plain", "utf-8")
        parte_html = MIMEText(texto_html, "html", "utf-8")
        msg.attach(parte_texto)
        msg.attach(parte_html)

        # Envia via SMTP
        logger.info(f"Conectando a SMTP {smtp_server}:{smtp_port} como {email_remetente}")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLS
            server.login(email_remetente, senha_email)
            server.send_message(msg)

        logger.info(f"Email de reset enviado para {email_destino}")
        return True, "Email enviado com sucesso! Verifique sua caixa de entrada."

    except smtplib.SMTPAuthenticationError:
        logger.error("Erro de autenticação SMTP - verifique email/senha/servidor.")
        return False, "Erro ao autenticar no servidor de email. Verifique credenciais."

    except smtplib.SMTPException as e:
        logger.error(f"Erro SMTP: {e}")
        return False, f"Erro ao enviar email: {str(e)}"

    except Exception as e:
        logger.error(f"Erro inesperado ao enviar email: {e}")
        return False, "Erro inesperado ao enviar email."
