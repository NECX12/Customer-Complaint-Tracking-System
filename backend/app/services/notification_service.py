"""
Notification service — creates notification records and enqueues Celery tasks.

The pattern is:
1. Create a Notification row in PostgreSQL with status=PENDING
2. Enqueue a Celery task with the notification ID
3. The Celery worker picks it up, sends the email, and updates the status

This decouples the API response time from email delivery.
If Celery/Redis is unavailable, the notification record still exists (PENDING)
and can be retried later.
"""

import logging
import uuid
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from sqlalchemy.orm import Session

from app.db.models.notification import Notification, NotificationStatus

logger = logging.getLogger(__name__)

# Load email templates from the templates directory
_template_env = Environment(
    loader=FileSystemLoader("app/templates/emails"),
    autoescape=True,
)


def _render_template(template_name: str, **kwargs) -> str:
    """Render an HTML email template. Falls back to plain text if template missing."""
    try:
        template = _template_env.get_template(template_name)
        return template.render(**kwargs)
    except TemplateNotFound:
        logger.warning(f"Email template not found: {template_name}")
        return f"Notification: {kwargs}"


def create_and_queue_notification(
    db: Session,
    user_id: uuid.UUID,
    complaint_id: Optional[uuid.UUID],
    notification_type: str,
    subject: str,
    template_name: str,
    template_data: Optional[dict] = None,
) -> Notification:
    """
    Create a notification record and enqueue it for async email delivery.

    The notification is persisted first (PENDING), then the Celery task is
    enqueued. If Redis is down, the notification still exists and can be
    picked up by a retry mechanism.
    """
    body = _render_template(template_name, **(template_data or {}))

    notification = Notification(
        user_id=user_id,
        complaint_id=complaint_id,
        notification_type=notification_type,
        subject=subject,
        body=body,
        status=NotificationStatus.PENDING,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Enqueue the Celery task — wrapped in try/except so a Redis failure
    # doesn't crash the API request
    try:
        from app.workers.tasks import send_email_notification
        send_email_notification.delay(str(notification.id))
        logger.info(f"Notification queued: {notification_type} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to enqueue notification task: {e}")
        # Notification record remains PENDING — can be retried

    return notification


# ── Convenience functions for specific notification types ────────────


def notify_complaint_submitted(
    db: Session, customer_id: uuid.UUID, complaint_id: uuid.UUID, title: str
) -> Notification:
    """Notify the customer that their complaint was received."""
    return create_and_queue_notification(
        db=db,
        user_id=customer_id,
        complaint_id=complaint_id,
        notification_type="COMPLAINT_SUBMITTED",
        subject=f"Complaint Received: {title}",
        template_name="complaint_submitted.html",
        template_data={"title": title, "complaint_id": str(complaint_id)},
    )


def notify_complaint_assigned(
    db: Session,
    agent_id: uuid.UUID,
    complaint_id: uuid.UUID,
    title: str,
    agent_name: str,
) -> Notification:
    """Notify the agent that a complaint has been assigned to them."""
    return create_and_queue_notification(
        db=db,
        user_id=agent_id,
        complaint_id=complaint_id,
        notification_type="COMPLAINT_ASSIGNED",
        subject=f"New Assignment: {title}",
        template_name="complaint_assigned.html",
        template_data={
            "title": title,
            "complaint_id": str(complaint_id),
            "agent_name": agent_name,
        },
    )


def notify_status_updated(
    db: Session,
    customer_id: uuid.UUID,
    complaint_id: uuid.UUID,
    title: str,
    old_status: str,
    new_status: str,
) -> Notification:
    """Notify the customer that their complaint status has changed."""
    return create_and_queue_notification(
        db=db,
        user_id=customer_id,
        complaint_id=complaint_id,
        notification_type="STATUS_UPDATED",
        subject=f"Complaint Update: {title}",
        template_name="status_updated.html",
        template_data={
            "title": title,
            "complaint_id": str(complaint_id),
            "old_status": old_status,
            "new_status": new_status,
        },
    )


def notify_complaint_resolved(
    db: Session,
    customer_id: uuid.UUID,
    complaint_id: uuid.UUID,
    title: str,
) -> Notification:
    """Notify the customer that their complaint has been resolved."""
    return create_and_queue_notification(
        db=db,
        user_id=customer_id,
        complaint_id=complaint_id,
        notification_type="COMPLAINT_RESOLVED",
        subject=f"Complaint Resolved: {title}",
        template_name="complaint_resolved.html",
        template_data={"title": title, "complaint_id": str(complaint_id)},
    )
