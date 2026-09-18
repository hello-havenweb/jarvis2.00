"""Email validation and sanitization utilities."""

import re
from typing import List, Tuple, Optional

# Basic RFC 5322 compliant regex for practical email validation
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)


class EmailValidationError(Exception):
    """Raised when an email address or list fails validation."""
    pass


def is_valid_email(address: str) -> bool:
    """Check whether an email address format is valid."""
    if not address or not isinstance(address, str):
        return False
    
    # Extract address if formatted as 'Name <email@example.com>'
    match = re.search(r"<([^>]+)>", address)
    target = match.group(1).strip() if match else address.strip()

    if len(target) > 254:
        return False

    return bool(EMAIL_REGEX.match(target))


def clean_address(address: str) -> str:
    """Clean whitespace and ensure address syntax."""
    return address.strip()


def validate_recipient_list(recipients: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of email addresses.
    
    Returns:
        Tuple of (valid_recipients, invalid_recipients)
    """
    valid: List[str] = []
    invalid: List[str] = []

    for r in recipients:
        cleaned = clean_address(r)
        if is_valid_email(cleaned):
            valid.append(cleaned)
        else:
            invalid.append(cleaned)

    return valid, invalid
