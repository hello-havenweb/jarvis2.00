"""End-to-end example demonstrating the email_module workflows."""

from datetime import datetime, timedelta, timezone
from email_module import (
    DraftManager,
    EmailSender,
    EmailScheduler,
    EmailTemplate,
    TemplateRegistry,
    SQLiteDraftStorage,
    SMTPConfig,
    EmailMessage,
    Attachment,
    EmailPriority,
)


def main():
    # 1. Setup Template Registry
    registry = TemplateRegistry()
    welcome_tmpl = EmailTemplate(
        name="welcome_user",
        subject_template="Welcome to the platform, $name!",
        body_text_template="Hi $name,\n\nThanks for joining us at $company_name.",
        body_html_template="<h2>Hi $name,</h2><p>Thanks for joining us at <b>$company_name</b>.</p>",
    )
    registry.register(welcome_tmpl)

    rendered = registry.render(
        "welcome_user",
        {"name": "Alice", "company_name": "Acme Corp"}
    )

    # 2. Draft Management & Storage
    storage = SQLiteDraftStorage(db_path="drafts.db")
    draft_mgr = DraftManager()

    draft = draft_mgr.create(
        subject=rendered["subject"],
        body_text=rendered["body_text"],
        body_html=rendered["body_html"],
        to_recipients=["alice@example.com"],
        reply_to="support@acme.com",
    )
    print(f"Created Draft ID: {draft.id}")

    # Persist draft to SQLite
    storage.save(draft)
    retrieved_draft = storage.get(draft.id)
    print(f"Retrieved from DB: {retrieved_draft.subject if retrieved_draft else 'Not found'}")

    # 3. Convert Draft to EmailMessage
    payload = draft_mgr.to_send_payload(draft.id)
    email_msg = EmailMessage(
        subject=payload["subject"],
        from_address="noreply@acme.com",
        to_recipients=payload["to"],
        body_text=payload["body_text"],
        body_html=payload["body_html"],
        reply_to=payload["reply_to"],
        priority=EmailPriority.HIGH,
        attachments=[
            Attachment(
                filename="welcome.txt",
                content=b"Welcome to Acme Corp! Here is your starter guide.",
            )
        ],
    )

    # 4. Configure SMTP Sender
    smtp_config = SMTPConfig(
        host="smtp.example.com",
        port=587,
        username="user@example.com",
        password="secretpassword",
        use_tls=True,
    )
    sender = EmailSender(smtp_config)

    # 5. Schedule Email for Future Sending
    scheduler = EmailScheduler(sender=sender, poll_interval=1.0)
    scheduler.start()

    send_time = datetime.now(timezone.utc) + timedelta(seconds=5)
    task_id = scheduler.schedule(email_msg, send_at=send_time)
    print(f"Scheduled email task ID: {task_id}")

    # Stop scheduler after running
    scheduler.stop()
    print("Workflow completed successfully.")


if __name__ == "__main__":
    main()
