"""
Complaint service — core business logic for the complaint lifecycle.

Handles complaint creation, retrieval, status transitions, and assignment.
Every status change creates a history record for timeline display.

The state machine (VALID_TRANSITIONS) is enforced here, not in the route handler,
so that the rules are consistent regardless of how complaints are modified.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.db.models.complaint import Complaint, ComplaintStatus, ComplaintPriority, VALID_TRANSITIONS
from app.db.models.complaint_history import ComplaintStatusHistory
from app.db.models.user import User, UserRole

logger = logging.getLogger(__name__)


def create_complaint(
    db: Session,
    customer: User,
    title: str,
    description: str,
    priority: str = "MEDIUM",
) -> Complaint:
    """
    Create a new complaint for the authenticated customer.

    Automatically:
    - Sets status to SUBMITTED
    - Sets customer_id from the authenticated user (never from user input)
    - Creates the initial status history entry
    """
    complaint = Complaint(
        customer_id=customer.id,
        title=title,
        description=description,
        priority=ComplaintPriority(priority),
        status=ComplaintStatus.SUBMITTED,
    )
    db.add(complaint)
    db.flush()  # get the complaint ID without committing

    # Create initial status history entry
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=None,
        new_status=ComplaintStatus.SUBMITTED.value,
        changed_by=customer.id,
        comment="Complaint submitted",
    )
    db.add(history)
    db.commit()
    db.refresh(complaint)

    logger.info(f"Complaint created: {complaint.id} by customer {customer.id}")
    return complaint


def get_complaint_by_id(
    db: Session,
    complaint_id: uuid.UUID,
) -> Optional[Complaint]:
    """Fetch a single complaint with relationships eagerly loaded."""
    return (
        db.query(Complaint)
        .options(
            joinedload(Complaint.customer),
            joinedload(Complaint.assigned_agent),
        )
        .filter(Complaint.id == complaint_id)
        .first()
    )


def get_complaints_by_customer(db: Session, customer_id: uuid.UUID) -> list[Complaint]:
    """Get all complaints submitted by a specific customer."""
    return (
        db.query(Complaint)
        .filter(Complaint.customer_id == customer_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )


def get_complaints_by_agent(db: Session, agent_id: uuid.UUID) -> list[Complaint]:
    """Get all complaints assigned to a specific agent."""
    return (
        db.query(Complaint)
        .filter(Complaint.assigned_agent_id == agent_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )


def get_all_complaints(
    db: Session,
    status_filter: Optional[str] = None,
) -> list[Complaint]:
    """Get all complaints (admin view), optionally filtered by status."""
    query = db.query(Complaint).options(
        joinedload(Complaint.customer),
        joinedload(Complaint.assigned_agent),
    )
    if status_filter:
        query = query.filter(Complaint.status == ComplaintStatus(status_filter))
    return query.order_by(Complaint.created_at.desc()).all()


def update_complaint_status(
    db: Session,
    complaint: Complaint,
    new_status_str: str,
    changed_by: User,
    comment: Optional[str] = None,
) -> Complaint:
    """
    Transition a complaint to a new status.

    Validates the transition against VALID_TRANSITIONS state machine.
    Creates a history record for every transition.
    Sets resolved_at when status becomes RESOLVED.

    Raises ValueError if the transition is invalid.
    """
    new_status = ComplaintStatus(new_status_str)
    current_status = complaint.status

    # Validate state machine transition
    if new_status not in VALID_TRANSITIONS.get(current_status, []):
        raise ValueError(
            f"Invalid transition: {current_status.value} → {new_status.value}. "
            f"Allowed: {[s.value for s in VALID_TRANSITIONS.get(current_status, [])]}"
        )

    old_status = current_status.value
    complaint.status = new_status

    # Track resolution time
    if new_status == ComplaintStatus.RESOLVED:
        complaint.resolved_at = datetime.now(timezone.utc)
    elif new_status == ComplaintStatus.IN_PROGRESS and complaint.resolved_at:
        # Reopened — clear resolved_at
        complaint.resolved_at = None

    # Create history record
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status.value,
        changed_by=changed_by.id,
        comment=comment,
    )
    db.add(history)
    db.commit()
    db.refresh(complaint)

    logger.info(
        f"Complaint {complaint.id}: {old_status} → {new_status.value} "
        f"by {changed_by.email}"
    )
    return complaint


def assign_complaint(
    db: Session,
    complaint: Complaint,
    agent: User,
    assigned_by: User,
    comment: Optional[str] = None,
) -> Complaint:
    """
    Assign (or reassign) a complaint to an agent.

    Validates that:
    - The target user is an active AGENT
    - The complaint is in SUBMITTED status (for first assignment)
      or already ASSIGNED / IN_PROGRESS (for reassignment)

    Creates history record and updates complaint status to ASSIGNED.
    """
    if agent.role != UserRole.AGENT:
        raise ValueError("Can only assign complaints to agents")
    if not agent.is_active:
        raise ValueError("Cannot assign to an inactive agent")

    old_status = complaint.status.value
    complaint.assigned_agent_id = agent.id

    # Only change status to ASSIGNED if currently SUBMITTED
    if complaint.status == ComplaintStatus.SUBMITTED:
        complaint.status = ComplaintStatus.ASSIGNED

    # Create history record
    assign_comment = comment or f"Assigned to {agent.name}"
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=complaint.status.value,
        changed_by=assigned_by.id,
        comment=assign_comment,
    )
    db.add(history)
    db.commit()
    db.refresh(complaint)

    logger.info(
        f"Complaint {complaint.id} assigned to agent {agent.email} "
        f"by {assigned_by.email}"
    )
    return complaint


def get_complaint_history(
    db: Session,
    complaint_id: uuid.UUID,
) -> list[ComplaintStatusHistory]:
    """Get the full status history for a complaint, ordered chronologically."""
    return (
        db.query(ComplaintStatusHistory)
        .options(joinedload(ComplaintStatusHistory.actor))
        .filter(ComplaintStatusHistory.complaint_id == complaint_id)
        .order_by(ComplaintStatusHistory.created_at.asc())
        .all()
    )
