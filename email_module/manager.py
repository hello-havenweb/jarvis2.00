"""Email management — coordinates IMAP and SMTP."""

from typing import List, Optional, Dict
from core.config import Config
from core.logger import get_logger
from core.models import ToolResult

logger = get_logger("email")


class EmailManager:
    """Manages email operations."""

    def __init__(self) -> None:
        self.config = Config()
        self._enabled = bool(self.config.env("EMAIL_IMAP_HOST") or self.config.get("email.imap_host"))

    @property
    def enabled(self) -> bool:
        return self._enabled

    def read_emails(self, folder: str = "INBOX", limit: int = 10) -> ToolResult:
        """Read recent emails."""
        if not self._enabled:
            return ToolResult(success=False, error="Email is not configured. Set EMAIL_* in .env file.")

        try:
            from email_module.imap_client import IMAPClient
            client = IMAPClient()
            emails = client.fetch_recent(folder=folder, limit=limit)
            if not emails:
                return ToolResult(success=True, message="No emails found.")

            lines = ["📧 Recent Emails:"]
            for e in emails:
                lines.append(f"  From: {e.get('from', 'Unknown')}")
                lines.append(f"  Subject: {e.get('subject', 'No subject')}")
                lines.append(f"  Date: {e.get('date', '')}")
                lines.append("  ---")

            return ToolResult(success=True, message="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=f"Email error: {e}")

    def send_email(self, to: str, subject: str, body: str) -> ToolResult:
        """Send an email."""
        if not self._enabled:
            return ToolResult(success=False, error="Email is not configured.")

        try:
            from email_module.smtp_client import SMTPClient
            client = SMTPClient()
            client.send(to=to, subject=subject, body=body)
            return ToolResult(success=True, message=f"📧 Email sent to {to}")
        except Exception as e:
            return ToolResult(success=False, error=f"Send email error: {e}")

    def search_emails(self, query: str) -> ToolResult:
        """Search emails."""
        if not self._enabled:
            return ToolResult(success=False, error="Email is not configured.")

        try:
            from email_module.imap_client import IMAPClient
            client = IMAPClient()
            results = client.search(query)
            if not results:
                return ToolResult(success=True, message=f"No emails found for: {query}")

            lines = [f"🔍 Email search results for '{query}':"]
            for e in results[:10]:
                lines.append(f"  From: {e.get('from', '')} | Subject: {e.get('subject', '')}")
            return ToolResult(success=True, message="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=f"Email search error: {e}")
