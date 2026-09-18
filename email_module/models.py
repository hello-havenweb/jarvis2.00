"""Data models and enums for email representation."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import mimetypes


class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class EmailStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    RECEIVED = "received"


@dataclass
class Attachment:
    """Represents a file attachment or inline object."""

    filename: str
    content: bytes
    content_type: Optional[str] = None
    content_id: Optional[str] = None
    is_inline: bool = False

    def __post_init__(self) -> None:
        if not self.content_type:
            mime_type, _ = mimetypes.guess_type(self.filename)
            self.content_type = mime_type or "application/octet-stream"

    @property
    def size_bytes(self) -> int:
        return len(self.content)


@dataclass
class EmailMessage:
    """Represents a fully structured email message."""

    subject: str
    from_address: str
    to_recipients: List[str] = field(default_factory=list)
    cc_recipients: List[str] = field(default_factory=list)
    bcc_recipients: List[str] = field(default_factory=list)
    reply_to: Optional[str] = None
    body_text: str = ""
    body_html: str = ""
    attachments: List[Attachment] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.QUEUED

    message_id: str = field(default_factory=lambda: f"<{uuid4()}@mail.local>")
    in_reply_to: Optional[str] = None
    references: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    @property
    def all_recipients(self) -> List[str]:
        """Combine all recipient addresses without duplicates while preserving order."""
        seen = set()
        recipients = []
        for r in self.to_recipients + self.cc_recipients + self.bcc_recipients:
            cleaned = r.strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                recipients.append(cleaned)
        return recipients
