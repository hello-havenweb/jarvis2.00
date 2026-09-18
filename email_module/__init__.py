"""JARVIS Email Package."""
"""Comprehensive Email Management Package."""

from .models import (
    EmailMessage,
    Attachment,
    EmailPriority,
    EmailStatus,
)
from .drafts import (
    Draft,
    DraftManager,
    DraftStatus,
    DraftError,
    DraftNotFoundError,
    DraftValidationError,
)
from .sender import (
    EmailSender,
    SMTPConfig,
    SenderError,
)
from .receiver import (
    EmailReceiver,
    IMAPConfig,
    ReceiverError,
)
from .templates import (
    EmailTemplate,
    TemplateRegistry,
    TemplateRenderError,
)
from .validator import (
    is_valid_email,
    validate_recipient_list,
    EmailValidationError,
)
from .storage import (
    BaseDraftStorage,
    SQLiteDraftStorage,
)
from .scheduler import (
    EmailScheduler,
    ScheduledEmail,
)

__all__ = [
    # Models
    "EmailMessage",
    "Attachment",
    "EmailPriority",
    "EmailStatus",
    # Drafts
    "Draft",
    "DraftManager",
    "DraftStatus",
    "DraftError",
    "DraftNotFoundError",
    "DraftValidationError",
    # Sending
    "EmailSender",
    "SMTPConfig",
    "SenderError",
    # Receiving
    "EmailReceiver",
    "IMAPConfig",
    "ReceiverError",
    # Templates
    "EmailTemplate",
    "TemplateRegistry",
    "TemplateRenderError",
    # Validation
    "is_valid_email",
    "validate_recipient_list",
    "EmailValidationError",
    # Storage
    "BaseDraftStorage",
    "SQLiteDraftStorage",
    # Scheduler
    "EmailScheduler",
    "ScheduledEmail",
]
