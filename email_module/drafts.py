"""Email draft management."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
from uuid import uuid4
from enum import Enum


class DraftStatus(str, Enum):
    """Status states for an email draft."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class DraftError(Exception):
    """Base exception for draft errors."""
    pass


class DraftNotFoundError(DraftError):
    """Raised when a requested draft cannot be found."""
    pass


class DraftValidationError(DraftError):
    """Raised when draft data fails validation."""
    pass


@dataclass
class Draft:
    """Represents an email draft."""

    id: str = field(default_factory=lambda: str(uuid4()))
    subject: str = ""
    body_text: str = ""
    body_html: str = ""
    to_recipients: List[str] = field(default_factory=list)
    cc_recipients: List[str] = field(default_factory=list)
    bcc_recipients: List[str] = field(default_factory=list)
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    status: DraftStatus = DraftStatus.DRAFT
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the draft to a dictionary."""
        return {
            "id": self.id,
            "subject": self.subject,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "to_recipients": list(self.to_recipients),
            "cc_recipients": list(self.cc_recipients),
            "bcc_recipients": list(self.bcc_recipients),
            "reply_to": self.reply_to,
            "attachments": list(self.attachments),
            "status": self.status.value,
            "thread_id": self.thread_id,
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Draft":
        """Deserialize a draft from a dictionary."""
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else data.get("created_at", datetime.now(timezone.utc))
        )
        updated_at = (
            datetime.fromisoformat(data["updated_at"])
            if isinstance(data.get("updated_at"), str)
            else data.get("updated_at", datetime.now(timezone.utc))
        )
        status = DraftStatus(data.get("status", DraftStatus.DRAFT.value))

        return cls(
            id=data.get("id", str(uuid4())),
            subject=data.get("subject", ""),
            body_text=data.get("body_text", ""),
            body_html=data.get("body_html", ""),
            to_recipients=list(data.get("to_recipients", [])),
            cc_recipients=list(data.get("cc_recipients", [])),
            bcc_recipients=list(data.get("bcc_recipients", [])),
            reply_to=data.get("reply_to"),
            attachments=list(data.get("attachments", [])),
            status=status,
            thread_id=data.get("thread_id"),
            metadata=dict(data.get("metadata", {})),
            created_at=created_at,
            updated_at=updated_at,
        )


class DraftManager:
    """Manages creation, retrieval, updates, and persistence of drafts."""

    def __init__(self) -> None:
        self._drafts: Dict[str, Draft] = {}

    def create(
        self,
        subject: str = "",
        body_text: str = "",
        body_html: str = "",
        to_recipients: Optional[List[str]] = None,
        cc_recipients: Optional[List[str]] = None,
        bcc_recipients: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Draft:
        """Create and store a new draft."""
        draft = Draft(
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            to_recipients=to_recipients or [],
            cc_recipients=cc_recipients or [],
            bcc_recipients=bcc_recipients or [],
            reply_to=reply_to,
            attachments=attachments or [],
            thread_id=thread_id,
            metadata=metadata or {},
        )
        self._drafts[draft.id] = draft
        return draft

    def get(self, draft_id: str) -> Draft:
        """Retrieve a draft by ID."""
        draft = self._drafts.get(draft_id)
        if not draft:
            raise DraftNotFoundError(f"Draft with ID '{draft_id}' not found.")
        return draft

    def update(
        self,
        draft_id: str,
        subject: Optional[str] = None,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        to_recipients: Optional[List[str]] = None,
        cc_recipients: Optional[List[str]] = None,
        bcc_recipients: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        status: Optional[DraftStatus] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Draft:
        """Update fields of an existing draft."""
        draft = self.get(draft_id)

        if subject is not None:
            draft.subject = subject
        if body_text is not None:
            draft.body_text = body_text
        if body_html is not None:
            draft.body_html = body_html
        if to_recipients is not None:
            draft.to_recipients = to_recipients
        if cc_recipients is not None:
            draft.cc_recipients = cc_recipients
        if bcc_recipients is not None:
            draft.bcc_recipients = bcc_recipients
        if reply_to is not None:
            draft.reply_to = reply_to
        if attachments is not None:
            draft.attachments = attachments
        if status is not None:
            draft.status = status
        if metadata is not None:
            draft.metadata.update(metadata)

        draft.touch()
        return draft

    def delete(self, draft_id: str) -> bool:
        """Delete a draft by ID. Returns True if deleted."""
        if draft_id not in self._drafts:
            raise DraftNotFoundError(f"Draft with ID '{draft_id}' not found.")
        del self._drafts[draft_id]
        return True

    def list_drafts(
        self,
        status: Optional[DraftStatus] = None,
        thread_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Draft]:
        """List drafts filtered by status and thread_id, sorted newest first."""
        results = list(self._drafts.values())

        if status is not None:
            results = [d for d in results if d.status == status]

        if thread_id is not None:
            results = [d for d in results if d.thread_id == thread_id]

        results.sort(key=lambda d: d.updated_at, reverse=True)

        if offset:
            results = results[offset:]
        if limit is not None:
            results = results[:limit]

        return results

    def duplicate(self, draft_id: str) -> Draft:
        """Clone an existing draft with a new ID."""
        original = self.get(draft_id)
        clone_dict = original.to_dict()
        clone_dict["id"] = str(uuid4())
        clone_dict["created_at"] = datetime.now(timezone.utc)
        clone_dict["updated_at"] = datetime.now(timezone.utc)

        new_draft = Draft.from_dict(clone_dict)
        self._drafts[new_draft.id] = new_draft
        return new_draft

    def to_send_payload(self, draft_id: str) -> Dict[str, Any]:
        """Validate and prepare a draft's contents for dispatching via an email sender."""
        draft = self.get(draft_id)

        all_recipients = draft.to_recipients + draft.cc_recipients + draft.bcc_recipients
        if not all_recipients:
            raise DraftValidationError("Draft has no recipients specified.")

        if not draft.body_text and not draft.body_html:
            raise DraftValidationError("Draft must contain either plain text or HTML body.")

        return {
            "draft_id": draft.id,
            "subject": draft.subject,
            "body_text": draft.body_text,
            "body_html": draft.body_html,
            "to": draft.to_recipients,
            "cc": draft.cc_recipients,
            "bcc": draft.bcc_recipients,
            "reply_to": draft.reply_to,
            "attachments": draft.attachments,
            "metadata": draft.metadata,
        }
