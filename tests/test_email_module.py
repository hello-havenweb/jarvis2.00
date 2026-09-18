"""Unit tests for the email_module package."""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import os

from email_module.models import EmailMessage, Attachment, EmailPriority, EmailStatus
from email_module.drafts import DraftManager, DraftStatus, DraftNotFoundError, DraftValidationError
from email_module.validator import is_valid_email, validate_recipient_list
from email_module.templates import EmailTemplate, TemplateRegistry, TemplateRenderError
from email_module.storage import SQLiteDraftStorage
from email_module.sender import EmailSender, SMTPConfig


class TestValidator(unittest.TestCase):
    def test_valid_emails(self):
        self.assertTrue(is_valid_email("user@example.com"))
        self.assertTrue(is_valid_email("user.name+tag@sub.domain.co"))
        self.assertTrue(is_valid_email("User Name <user@example.com>"))

    def test_invalid_emails(self):
        self.assertFalse(is_valid_email("plainaddress"))
        self.assertFalse(is_valid_email("@missingusername.com"))
        self.assertFalse(is_valid_email("username@.com"))
        self.assertFalse(is_valid_email(""))

    def test_validate_recipient_list(self):
        recipients = ["good@test.com", "bad-email", "another.good@test.org"]
        valid, invalid = validate_recipient_list(recipients)
        self.assertEqual(len(valid), 2)
        self.assertEqual(len(invalid), 1)
        self.assertEqual(invalid[0], "bad-email")


class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.registry = TemplateRegistry()
        self.template = EmailTemplate(
            name="test_tmpl",
            subject_template="Hello $name",
            body_text_template="Body for $name at $org",
            body_html_template="<p>Body for $name at $org</p>",
        )
        self.registry.register(self.template)

    def test_render_success(self):
        result = self.registry.render("test_tmpl", {"name": "Bob", "org": "ACME"})
        self.assertEqual(result["subject"], "Hello Bob")
        self.assertEqual(result["body_text"], "Body for Bob at ACME")
        self.assertEqual(result["body_html"], "<p>Body for Bob at ACME</p>")

    def test_render_missing_variable_raises(self):
        with self.assertRaises(TemplateRenderError):
            self.registry.render("test_tmpl", {"name": "Bob"})

    def test_render_safe(self):
        result = self.registry.render("test_tmpl", {"name": "Bob"}, safe=True)
        self.assertEqual(result["body_text"], "Body for Bob at $org")


class TestDrafts(unittest.TestCase):
    def setUp(self):
        self.manager = DraftManager()

    def test_create_and_get_draft(self):
        draft = self.manager.create(
            subject="Test Draft",
            body_text="Hello world",
            to_recipients=["test@example.com"],
        )
        fetched = self.manager.get(draft.id)
        self.assertEqual(fetched.subject, "Test Draft")
        self.assertEqual(fetched.status, DraftStatus.DRAFT)

    def test_update_draft(self):
        draft = self.manager.create(subject="Old Subject")
        updated = self.manager.update(draft.id, subject="New Subject", status=DraftStatus.SCHEDULED)
        self.assertEqual(updated.subject, "New Subject")
        self.assertEqual(updated.status, DraftStatus.SCHEDULED)

    def test_delete_draft(self):
        draft = self.manager.create(subject="To Delete")
        self.manager.delete(draft.id)
        with self.assertRaises(DraftNotFoundError):
            self.manager.get(draft.id)

    def test_payload_validation_fails_without_recipients(self):
        draft = self.manager.create(subject="No recipients", body_text="Hello")
        with self.assertRaises(DraftValidationError):
            self.manager.to_send_payload(draft.id)


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_drafts.db"
        self.storage = SQLiteDraftStorage(self.db_path)
        self.manager = DraftManager()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_retrieve(self):
        draft = self.manager.create(
            subject="Persistent Draft",
            body_text="Saved in SQLite",
            to_recipients=["db@example.com"],
        )
        self.storage.save(draft)
        retrieved = self.storage.get(draft.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.subject, "Persistent Draft")
        self.assertEqual(retrieved.to_recipients, ["db@example.com"])


class TestSender(unittest.TestCase):
    @patch("smtplib.SMTP")
    def test_send_success(self, mock_smtp_cls):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        config = SMTPConfig(host="localhost", port=25, use_tls=False)
        sender = EmailSender(config)

        msg = EmailMessage(
            subject="Test subject",
            from_address="sender@example.com",
            to_recipients=["receiver@example.com"],
            body_text="Plain message text",
        )

        success = sender.send(msg)
        self.assertTrue(success)
        self.assertEqual(msg.status, EmailStatus.SENT)
        mock_server.sendmail.assert_called_once()


if __name__ == "__main__":
    unittest.main()
