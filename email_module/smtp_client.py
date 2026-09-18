"""SMTP email client for sending emails."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config import Config
from core.logger import get_logger

logger = get_logger("smtp")


class SMTPClient:
    """SMTP client for sending emails."""

    def __init__(self) -> None:
        self.config = Config()
        self.host = self.config.env("EMAIL_SMTP_HOST", self.config.get("email.smtp_host", ""))
        self.port = self.config.env_int("EMAIL_SMTP_PORT", self.config.get("email.smtp_port", 587))
        self.username = self.config.env("EMAIL_USERNAME", self.config.get("email.username", ""))
        self.password = self.config.env("EMAIL_PASSWORD", "")

    def send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """Send an email."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = to
            msg["Subject"] = subject

            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type, "utf-8"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent to {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"SMTP send error: {e}")
            raise
