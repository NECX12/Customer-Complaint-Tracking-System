"""
Notification tests — verifies notification records are created correctly.

These tests verify the notification service creates records; they do NOT
test actual email delivery (which requires a running Celery worker and SMTP).
The Celery task is mocked to avoid requiring Redis during tests.
"""

from unittest.mock import patch

from tests.conftest import get_auth_headers
from app.db.models.notification import Notification, NotificationStatus


class TestNotifications:
    """Notification creation tests."""

    @patch("app.workers.tasks.send_email_notification")
    def test_complaint_creates_notification(self, mock_task, client, db, customer):
        """Submitting a complaint should create a PENDING notification."""
        headers = get_auth_headers(customer)
        response = client.post("/api/v1/complaints", headers=headers, json={
            "title": "Notification test complaint",
            "description": "This should trigger a notification",
        })
        assert response.status_code == 201

        # Check notification was created in the database
        notifications = db.query(Notification).filter(
            Notification.user_id == customer.id,
            Notification.notification_type == "COMPLAINT_SUBMITTED",
        ).all()
        assert len(notifications) == 1
        assert notifications[0].status == NotificationStatus.PENDING

    @patch("app.workers.tasks.send_email_notification")
    def test_notification_has_correct_subject(self, mock_task, client, db, customer):
        """Notification subject should reference the complaint title."""
        headers = get_auth_headers(customer)
        title = "Broken Generator XYZ"
        client.post("/api/v1/complaints", headers=headers, json={
            "title": title,
            "description": "Detailed description of the problem here",
        })

        notification = db.query(Notification).filter(
            Notification.user_id == customer.id,
        ).first()
        assert title in notification.subject

    @patch("app.workers.tasks.send_email_notification")
    def test_celery_task_is_enqueued(self, mock_task, client, customer):
        """The send_email_notification Celery task should be called."""
        headers = get_auth_headers(customer)
        client.post("/api/v1/complaints", headers=headers, json={
            "title": "Task queue test",
            "description": "This should enqueue a Celery task",
        })
        mock_task.delay.assert_called_once()
