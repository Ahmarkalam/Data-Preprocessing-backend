import os
import smtplib
from email.message import EmailMessage
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger("email_service")

def _get_smtp_config():
    return {
        "host": os.getenv("SMTP_HOST"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASS"),
        "from_email": os.getenv("SMTP_FROM", os.getenv("SMTP_USER")),
        "use_tls": os.getenv("SMTP_TLS", "true").lower() not in ["false", "0", "no"]
    }

def send_access_email(to_email: str, api_key: str, access_link: str) -> bool:
    """
    MVP email sender:
    - Uses SMTP if configured via environment variables.
    - Falls back to logging-only mode when SMTP is not configured.
    """
    cfg = _get_smtp_config()
    subject = "Your DataPrep access link"
    body = (
        "Hello,\n\n"
        "Here is your access information:\n\n"
        f"API Key: {api_key}\n"
        f"Access your dashboard: {access_link}\n\n"
        "This link is valid for 24 hours and can be used once.\n\n"
        "— DataPrep AI\n"
    )

    if not cfg["host"] or not cfg["from_email"]:
        logger.warning("SMTP not configured; printing email content for development.")
        logger.info(f"To: {to_email}\nSubject: {subject}\n\n{body}")
        return True

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = cfg["from_email"]
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(cfg["host"], cfg["port"]) as smtp:
            if cfg["use_tls"]:
                smtp.starttls()
            if cfg["user"] and cfg["password"]:
                smtp.login(cfg["user"], cfg["password"])
            smtp.send_message(msg)

        logger.info(f"Access email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
