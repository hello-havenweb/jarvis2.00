"""IMAP Email Receiver for fetching and reading incoming emails."""

import imaplib
import email
from email.header import decode_header
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
import logging

from .models import EmailMessage, Attachment, EmailStatus

logger = logging.getLogger(__name__)


@dataclass
class IMAPConfig:
    """Configuration for IMAP client connection."""
    host: str
    port: int = 993
    username: str = ""
    password: str = ""
    use_ssl: bool = True
    timeout: float = 30.0


class ReceiverError(Exception):
    """Base exception for email retrieval errors."""
    pass


class EmailReceiver:
    """Handles fetching and parsing emails from an IMAP server."""

    def __init__(self, config: IMAPConfig) -> None:
        self.config = config
        self._connection: Optional[imaplib.IMAP4] = None

    def connect(self) -> None:
        """Connect and login to the IMAP server."""
        try:
            if self.config.use_ssl:
                self._connection = imaplib.IMAP4_SSL(
                    self.config.host, self.config.port
                )
            else:
                self._connection = imaplib.IMAP4(
                    self.config.host, self.config.port
                )
            self._connection.login(self.config.username, self.config.password)
        except Exception as e:
            raise ReceiverError(f"IMAP connection failed: {e}") from e

    def disconnect(self) -> None:
        """Close folder and log out."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            try:
                self._connection.logout()
            except Exception:
                pass
            self._connection = None

    def _decode_str(self, header_val: Optional[str]) -> str:
        """Safely decode RFC2047 encoded email headers."""
        if not header_val:
            return ""
        decoded_parts = decode_header(header_val)
        result = []
        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                result.append(content.decode(encoding or "utf-8", errors="replace"))
            else:
                result.append(str(content))
        return "".join(result)

    def _parse_email(self, raw_bytes: bytes) -> EmailMessage:
        """Parse raw email bytes into an EmailMessage object."""
        msg = email.message_from_bytes(raw_bytes)

        subject = self._decode_str(msg.get("Subject", ""))
        from_addr = self._decode_str(msg.get("From", ""))
        to_addrs = [self._decode_str(x) for x in msg.get_all("To", [])]
        cc_addrs = [self._decode_str(x) for x in msg.get_all("Cc", [])]
        message_id = msg.get("Message-ID", "")
        in_reply_to = msg.get("In-Reply-To")

        body_text = ""
        body_html = ""
        attachments: List[Attachment] = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                filename = part.get_filename()

                if filename or "attachment" in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        attachments.append(
                            Attachment(
                                filename=self._decode_str(filename) or "unnamed_attachment",
                                content=payload,
                                content_type=content_type,
                                is_inline="inline" in content_disposition,
                            )
                        )
                elif content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_text += payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_html += payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        else:
            payload = msg.get_payload(decode=True)
            text = payload.decode(msg.get_content_charset() or "utf-8", errors="replace") if payload else ""
            if msg.get_content_type() == "text/html":
                body_html = text
            else:
                body_text = text

        return EmailMessage(
            subject=subject,
            from_address=from_addr,
            to_recipients=to_addrs,
            cc_recipients=cc_addrs,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            message_id=message_id,
            in_reply_to=in_reply_to,
            status=EmailStatus.RECEIVED,
        )

    def fetch_unread(self, folder: str = "INBOX", limit: Optional[int] = None) -> List[EmailMessage]:
        """Fetch unread emails from the specified folder."""
        if not self._connection:
            self.connect()

        assert self._connection is not None
        self._connection.select(folder)
        status, response = self._connection.search(None, "UNSEEN")
        if status != "OK":
            return []

        message_ids = response[0].split()
        if limit:
            message_ids = message_ids[-limit:]

        messages: List[EmailMessage] = []
        for msg_id in message_ids:
            res_status, msg_data = self._connection.fetch(msg_id, "(RFC822)")
            if res_status == "OK" and msg_data and isinstance(msg_data[0], tuple):
                raw_email = msg_data[0][1]
                messages.append(self._parse_email(raw_email))

        return messages
