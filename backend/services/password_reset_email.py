import logging
import smtplib
from email.message import EmailMessage

from config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_FROM:
        return False
    msg = EmailMessage()
    msg["Subject"] = "Reset your AI Receptionist password"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        f"You requested a password reset.\n\nOpen this link (valid for "
        f"{settings.PASSWORD_RESET_TOKEN_HOURS} hour(s)):\n{reset_url}\n\n"
        "If you did not request this, ignore this email."
    )
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as smtp:
            smtp.starttls()
            if settings.SMTP_USER:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except OSError as e:
        logger.error("SMTP send failed: %s", e)
        return False
