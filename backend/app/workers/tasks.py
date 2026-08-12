"""
Celery tasks for asynchronous email notifications.

The main task (send_email_notification) is enqueued by the notification service
after creating a Notification record with PENDING status. The task:
1. Fetches the notification and user from the database
2. Sends the email via SMTP (or logs to console in dev mode)
3. Updates the notification status to SENT or FAILED

If SMTP is not configured, emails are logged to the console so the application
works in development without requiring an email provider.
"""

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.db.models.notification import Notification, NotificationStatus
from app.db.models.user import User
from app.db.session import SessionLocal
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="app.workers.tasks.send_email_notification",
)
def send_email_notification(self, notification_id: str) -> dict:
    """
    Send an email notification asynchronously.

    Retries up to 3 times with a 60-second delay between attempts.
    On final failure, the notification status is set to FAILED.
    """
    db = SessionLocal()
    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return {"status": "error", "detail": "Notification not found"}

        user = db.query(User).filter(User.id == notification.user_id).first()
        if not user:
            logger.error(f"User for notification {notification_id} not found")
            return {"status": "error", "detail": "User not found"}

        # Development mode: log instead of sending
        if not settings.email_enabled:
            logger.info(
                f"[DEV MODE] Email notification:\n"
                f"  To:      {user.email}\n"
                f"  Subject: {notification.subject}\n"
                f"  Type:    {notification.notification_type}\n"
                f"  Body:    {(notification.body or '')[:200]}..."
            )
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            db.commit()
            return {"status": "sent", "mode": "dev"}

        # Production: send via SMTP
        _send_smtp_email(
            to_email=user.email,
            subject=notification.subject,
            body=notification.body or "",
        )

        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Email sent: {notification.notification_type} to {user.email}")
        return {"status": "sent", "mode": "smtp"}

    except Exception as exc:
        db.rollback()

        # Update status to FAILED on final retry
        try:
            if self.request.retries >= self.max_retries:
                notification = (
                    db.query(Notification)
                    .filter(Notification.id == notification_id)
                    .first()
                )
                if notification:
                    notification.status = NotificationStatus.FAILED
                    db.commit()
                logger.error(
                    f"Notification {notification_id} failed permanently: {exc}"
                )
            else:
                logger.warning(
                    f"Notification {notification_id} failed, retrying: {exc}"
                )
        except Exception:
            pass

        raise self.retry(exc=exc)

    finally:
        db.close()


def _send_smtp_email(to_email: str, subject: str, body: str) -> None:
    """Send an HTML email via the configured SMTP server."""
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
