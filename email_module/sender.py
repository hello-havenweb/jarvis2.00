"""SMTP Email Sender engine with TLS/SSL, attachments, and retry support."""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass

from .models import EmailMessage, Attachment, EmailStatus, EmailPriority
from .validator import validate_recipient_list, EmailValidationError

logger = logging.getLogger(__name__)


@dataclass
class SMTPConfig:
    """Configuration for SMTP client connection."""
    host: str
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True
    use_ssl: bool = False
    timeout: float = 30.0


class SenderError(Exception):
    """Base exception for email sending errors."""
    pass


class EmailSender:
    """Handles sending email messages via standard SMTP."""

    def __init__(self, config: SMTPConfig) -> None:
        self.config = config

    def _create_connection(self) -> smtplib.SMTP:
        """Create and authenticate an SMTP connection."""
        if self.config.use_ssl:
            server = smtplib.SMTP_SSL(self.config.host, self.config.port, timeout=self.config.timeout)
        else:
            server = smtplib.SMTP(self.config.host, self.config.port, timeout=self.config.timeout)

        server.ehlo()

        if self.config.use_tls and not self.config.use_ssl:
            server.starttls()
            server.ehlo()

        if self.config.username and self.config.password:
            server.login(self.config.username, self.config.password)

        return server

    def _build_mime_message(self, message: EmailMessage) -> MIMEMultipart:
        """Converts an EmailMessage dataclass into a python MIME object."""
        # Top-level container
        if message.attachments:
            msg = MIMEMultipart("mixed")
            body_container = MIMEMultipart("alternative")
            msg.attach(body_container)
        else:
            msg = MIMEMultipart("alternative")
            body_container = msg

        # Headers
        msg["Subject"] = message.subject
        msg["From"] = message.from_address
        msg["To"] = ", ".join(message.to_recipients)
        if message.cc_recipients:
            msg["Cc"] = ", ".join(message.cc_recipients)
        if message.reply_to:
            msg["Reply-To"] = message.reply_to
        if message.message_id:
            msg["Message-ID"] = message.message_id
        if message.in_reply_to:
            msg["In-Reply-To"] = message.in_reply_to
        if message.references:
            msg["References"] = " ".join(message.references)

        # Priority headers
        if message.priority == EmailPriority.HIGH:
            msg["X-Priority"] = "1"
            msg["Importance"] = "high"
        elif message.priority == EmailPriority.LOW:
            msg["X-Priority"] = "5"
            msg["Importance"] = "low"

        # Custom headers
        for k, v in message.headers.items():
            msg[k] = v

        # Bodies
        if message.body_text:
            body_container.attach(MIMEText(message.body_text, "plain", "utf-8"))
        if message.body_html:
            body_container.attach(MIMEText(message.body_html, "html", "utf-8"))

        # Attachments
        for att in message.attachments:
            maintype, subtype = (att.content_type or "application/octet-stream").split("/", 1)
            part = MIMEBase(maintype, subtype)
            part.set_payload(att.content)
            encoders.encode_base64(part)

            disposition = "inline" if att.is_inline else "attachment"
            part.add_header(
                "Content-Disposition",
                f'{disposition}; filename="{att.filename}"'
            )
            if att.content_id:
                part.add_header("Content-ID", f"<{att.content_id}>")

            msg.attach(part)

        return msg

    def test_connection(self) -> bool:
        """Test if the SMTP server is reachable and credentials are valid."""
        try:
            with self._create_connection() as server:
                server.noop()
            return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False

    def send(self, message: EmailMessage) -> bool:
        """Send an EmailMessage instance."""
        valid, invalid = validate_recipient_list(message.all_recipients)
        if invalid:
            raise EmailValidationError(f"Invalid email addresses found: {invalid}")
        if not valid:
            raise EmailValidationError("No valid recipients provided.")

        message.status = EmailStatus.SENDING
        mime_msg = self._build_mime_message(message)

        try:
            with self._create_connection() as server:
                server.sendmail(
                    from_addr=message.from_address,
                    to_addrs=message.all_recipients,
                    msg=mime_msg.as_string(),
                )
            message.status = EmailStatus.SENT
            message.sent_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            message.status = EmailStatus.FAILED
            message.error_message = str(e)
            logger.error(f"Failed to send email '{message.subject}': {e}")
            raise SenderError(f"Failed to dispatch email: {e}") from e
