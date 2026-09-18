"""JARVIS Main Assistant Runner."""

import os
import sys
from dotenv import load_dotenv

# Environment variables load karein
load_dotenv()

# Hamara email module import karein
from email_module import (
    EmailSender,
    EmailReceiver,
    EmailScheduler,
    DraftManager,
    SQLiteDraftStorage,
    SMTPConfig,
    IMAPConfig,
    EmailMessage,
)


class JarvisAssistant:
    def __init__(self):
        self.name = os.getenv("ASSISTANT_NAME", "JARVIS")
        self.user = os.getenv("USER_NAME", "Sir")

        # Storage & Drafts init
        self.storage = SQLiteDraftStorage(os.getenv("DB_PATH", "jarvis_data.db"))
        self.drafts = DraftManager()

        # SMTP Sender setup
        self.smtp_cfg = SMTPConfig(
            host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            port=int(os.getenv("SMTP_PORT", 587)),
            username=os.getenv("SMTP_USER", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            use_tls=True,
        )
        self.sender = EmailSender(self.smtp_cfg)

        # Scheduler start
        self.scheduler = EmailScheduler(sender=self.sender)
        self.scheduler.start()

    def greet(self):
        print(f"[{self.name}]: Systems Online. Ready for your commands, {self.user}.")

    def send_quick_email(self, to: str, subject: str, message: str):
        """Quick email helper."""
        email = EmailMessage(
            subject=subject,
            from_address=self.smtp_cfg.username or "jarvis@local",
            to_recipients=[to],
            body_text=message,
        )
        print(f"[{self.name}]: Dispatching email to {to}...")
        self.sender.send(email)
        print(f"[{self.name}]: Email successfully sent.")

    def shutdown(self):
        print(f"[{self.name}]: Shutting down background tasks...")
        self.scheduler.stop()
        print(f"[{self.name}]: Goodbye {self.user}.")


def main():
    jarvis = JarvisAssistant()
    jarvis.greet()

    try:
        while True:
            cmd = input(f"\n({jarvis.user}) > ").strip()
            if not cmd:
                continue

            if cmd.lower() in ["exit", "quit", "bye"]:
                jarvis.shutdown()
                break

            elif cmd.lower().startswith("email test"):
                jarvis.send_quick_email(
                    to="test@example.com",
                    subject="JARVIS System Test",
                    message="All modules are functioning properly, Sir.",
                )

            else:
                print(f"[{jarvis.name}]: Executing command -> '{cmd}'")

    except KeyboardInterrupt:
        jarvis.shutdown()


if __name__ == "__main__":
    main()
