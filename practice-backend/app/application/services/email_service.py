from __future__ import annotations

from dataclasses import dataclass
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.infrastructure.models import Notification

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailSendResult:
    status: str
    detail: str


class EmailService:
    def is_configured(self) -> bool:
        return bool(
            settings.EMAIL_NOTIFICATIONS_ENABLED
            and settings.SMTP_HOST
            and settings.SMTP_FROM_EMAIL
        )

    def send_test_email(self, *, to_email: str) -> EmailSendResult:
        return self._send(
            to_email=to_email,
            subject="Smart Plant Monitor test email",
            body=(
                "This is a test email from Smart Plant Monitor. "
                "Email notifications are configured for this contact."
            ),
        )

    def send_notification_email(self, *, to_email: str, notification: Notification) -> EmailSendResult:
        title = notification.title or "Smart Plant notification"
        body = self._notification_body(notification)
        return self._send(to_email=to_email, subject=title, body=body)

    def _notification_body(self, notification: Notification) -> str:
        lines = [
            notification.title or "Smart Plant notification",
            "",
            notification.message or "A new plant notification was created.",
            "",
            f"Priority: {notification.severity.value}",
        ]
        lines.extend(
            [
                "",
                "Open the Smart Plant web app to review the plant status and care recommendation.",
            ]
        )
        return "\n".join(lines)

    def _send(self, *, to_email: str, subject: str, body: str) -> EmailSendResult:
        if not settings.EMAIL_NOTIFICATIONS_ENABLED:
            logger.info("Email notifications disabled; logged email to %s subject=%s", to_email, subject)
            return EmailSendResult(status="disabled", detail="Email notifications are disabled.")
        if not self.is_configured():
            logger.info("SMTP not configured; logged email to %s subject=%s body=%s", to_email, subject, body)
            return EmailSendResult(status="logged", detail="SMTP is not configured; email was logged only.")

        message = EmailMessage()
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
                if settings.SMTP_USE_TLS:
                    smtp.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(message)
        except Exception as exc:
            logger.exception("Failed to send email notification to %s", to_email)
            return EmailSendResult(status="failed", detail=f"Email send failed: {exc}")

        return EmailSendResult(status="sent", detail="Email sent.")
