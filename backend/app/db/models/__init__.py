"""
Import all models so that Alembic and SQLAlchemy can discover them.

When Alembic runs autogenerate, it needs all models imported so that
Base.metadata contains all table definitions. This module centralizes
those imports.
"""

from app.db.models.user import User, UserRole  # noqa: F401
from app.db.models.complaint import (  # noqa: F401
    Complaint,
    ComplaintStatus,
    ComplaintPriority,
    VALID_TRANSITIONS,
)
from app.db.models.complaint_history import ComplaintStatusHistory  # noqa: F401
from app.db.models.notification import Notification, NotificationStatus  # noqa: F401
from app.db.models.audit_log import AuditLog  # noqa: F401
