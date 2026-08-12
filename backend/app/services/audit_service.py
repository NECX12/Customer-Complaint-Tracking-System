"""
Audit service — records important administrative actions.

Every significant action (user creation, complaint assignment, status change)
creates an audit log entry. This provides traceability for compliance and
debugging.

The details column accepts arbitrary JSON, so the schema doesn't need to change
when new action types are added.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    actor_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: Optional[uuid.UUID] = None,
    details: Optional[dict] = None,
) -> AuditLog:
    """
    Create an audit log entry.

    Args:
        actor_id: The user who performed the action.
        action: Action identifier (e.g., COMPLAINT_ASSIGNED, ADMIN_CREATED_AGENT).
        entity_type: The type of entity affected (e.g., "complaint", "user").
        entity_id: The ID of the affected entity.
        details: Optional JSON metadata with additional context.
    """
    audit = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    logger.info(f"Audit: {action} on {entity_type}/{entity_id} by {actor_id}")
    return audit
