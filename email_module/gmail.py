"""Gmail-specific helpers."""

from core.logger import get_logger

logger = get_logger("gmail")


class GmailHelper:
    """Gmail-specific configuration helper."""

    IMAP_HOST = "imap.gmail.com"
    IMAP_PORT = 993
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    @staticmethod
    def get_setup_instructions() -> str:
        """Return Gmail setup instructions."""
        return """
Gmail Setup Instructions:
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select 'Mail' and 'Windows Computer'
   - Copy the generated password
3. Set in .env:
   EMAIL_IMAP_HOST=imap.gmail.com
   EMAIL_IMAP_PORT=993
   EMAIL_SMTP_HOST=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_USERNAME=your.email@gmail.com
   EMAIL_PASSWORD=your_app_password
"""
