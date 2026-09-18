"""IMAP email client."""

import imaplib
import email as email_lib
from email.header import decode_header
from typing import List, Dict, Optional

from core.config import Config
from core.logger import get_logger

logger = get_logger("imap")


class IMAPClient:
    """IMAP email client for reading emails."""

    def __init__(self) -> None:
        self.config = Config()
        self.host = self.config.env("EMAIL_IMAP_HOST", self.config.get("email.imap_host", ""))
        self.port = self.config.env_int("EMAIL_IMAP_PORT", self.config.get("email.imap_port", 993))
        self.username = self.config.env("EMAIL_USERNAME", self.config.get("email.username", ""))
        self.password = self.config.env("EMAIL_PASSWORD", "")

    def _connect(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server."""
        conn = imaplib.IMAP4_SSL(self.host, self.port)
        conn.login(self.username, self.password)
        return conn

    def fetch_recent(self, folder: str = "INBOX", limit: int = 10) -> List[Dict]:
        """Fetch recent emails."""
        try:
            conn = self._connect()
            conn.select(folder)

            _, data = conn.search(None, "ALL")
            ids = data[0].split()
            ids = ids[-limit:] if len(ids) > limit else ids

            results = []
            for eid in reversed(ids):
                _, msg_data = conn.fetch(eid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email_lib.message_from_bytes(raw)

                subject = self._decode_header(msg.get("Subject", ""))
                from_addr = self._decode_header(msg.get("From", ""))
                date = msg.get("Date", "")

                results.append({
                    "from": from_addr,
                    "subject": subject,
                    "date": date,
                    "id": eid.decode()
                })

            conn.logout()
            return results
        except Exception as e:
            logger.error(f"IMAP fetch error: {e}")
            return []

    def search(self, query: str) -> List[Dict]:
        """Search emails."""
        try:
            conn = self._connect()
            conn.select("INBOX")

            _, data = conn.search(None, f'(SUBJECT "{query}")')
            ids = data[0].split()[:10]

            results = []
            for eid in reversed(ids):
                _, msg_data = conn.fetch(eid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email_lib.message_from_bytes(raw)

                results.append({
                    "from": self._decode_header(msg.get("From", "")),
                    "subject": self._decode_header(msg.get("Subject", "")),
                    "date": msg.get("Date", ""),
                })

            conn.logout()
            return results
        except Exception as e:
            logger.error(f"IMAP search error: {e}")
            return []

    @staticmethod
    def _decode_header(value: str) -> str:
        """Decode email header."""
        try:
            decoded_parts = decode_header(value)
            parts = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    parts.append(part.decode(encoding or "utf-8", errors="replace"))
                else:
                    parts.append(part)
            return " ".join(parts)
        except Exception:
            return str(value)
