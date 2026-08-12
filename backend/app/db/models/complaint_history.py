"""
Complaint status history — records every status transition for timeline display.

Each row captures: what changed, who changed it, and an optional comment.
The frontend uses this table to render a chronological complaint timeline.

Design decision: old_status and new_status are stored as String(50) rather than
reusing the ComplaintStatus PostgreSQL enum. This avoids shared-enum issues between
tables and makes history rows immutable snapshots — if the enum changes in the future,
historical records remain valid.
"""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ComplaintStatusHistory(Base, TimestampMixin):
    """
    Immutable record of a complaint status transition.

    The first entry for any complaint has old_status=None (initial submission).
    """

    __tablename__ = "complaint_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False, index=True
    )
    old_status: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True  # None for the first entry
    )
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    complaint = relationship("Complaint", back_populates="status_history")
    actor = relationship("User", foreign_keys=[changed_by])

    def __repr__(self) -> str:
        return f"<StatusHistory {self.old_status} → {self.new_status}>"
