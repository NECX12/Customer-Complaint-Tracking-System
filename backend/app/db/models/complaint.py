"""
Complaint model with status lifecycle and priority levels.

The status field on the complaint table holds the *current* status for fast queries,
while the full transition history is stored in complaint_status_history (see
complaint_history.py). This avoids expensive subqueries for simple status filters.

VALID_TRANSITIONS defines the complaint state machine — the service layer checks
this dict before allowing any status change.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ComplaintStatus(str, enum.Enum):
    """Complaint lifecycle states."""
    SUBMITTED = "SUBMITTED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class ComplaintPriority(str, enum.Enum):
    """Complaint priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── State Machine ────────────────────────────────────────────────────────
# Maps each status to the list of statuses it can transition to.
# Enforced in complaint_service.py before any status update.
VALID_TRANSITIONS: dict[ComplaintStatus, list[ComplaintStatus]] = {
    ComplaintStatus.SUBMITTED:   [ComplaintStatus.ASSIGNED],
    ComplaintStatus.ASSIGNED:    [ComplaintStatus.IN_PROGRESS],
    ComplaintStatus.IN_PROGRESS: [ComplaintStatus.RESOLVED],
    ComplaintStatus.RESOLVED:    [ComplaintStatus.CLOSED, ComplaintStatus.IN_PROGRESS],
    ComplaintStatus.CLOSED:      [],  # terminal state
}


class Complaint(Base, TimestampMixin):
    """Customer complaint with status tracking and agent assignment."""

    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    assigned_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus, name="complaintstatus"),
        nullable=False,
        default=ComplaintStatus.SUBMITTED,
        index=True,
    )
    priority: Mapped[ComplaintPriority] = mapped_column(
        Enum(ComplaintPriority, name="complaintpriority"),
        nullable=False,
        default=ComplaintPriority.MEDIUM,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    customer = relationship(
        "User", back_populates="submitted_complaints", foreign_keys=[customer_id]
    )
    assigned_agent = relationship(
        "User", back_populates="assigned_complaints", foreign_keys=[assigned_agent_id]
    )
    status_history = relationship(
        "ComplaintStatusHistory",
        back_populates="complaint",
        order_by="ComplaintStatusHistory.created_at",
    )

    def __repr__(self) -> str:
        return f"<Complaint {self.id} [{self.status.value}]>"
