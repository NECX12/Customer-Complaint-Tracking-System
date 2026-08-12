"""
User model — supports CUSTOMER, AGENT, and ADMIN roles.

The role is stored as a PostgreSQL enum for type safety at the database level.
Relationships are defined for both submitted complaints (as customer) and
assigned complaints (as agent), using explicit foreign_keys to disambiguate.
"""

import enum
import uuid

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    """
    System roles. Using str mixin so the enum serializes to its string value
    in Pydantic schemas and JSON responses.
    """
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"


class User(Base, TimestampMixin):
    """User account — customers, agents, and administrators."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole"), nullable=False, default=UserRole.CUSTOMER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships — explicit foreign_keys because User relates to Complaint twice
    submitted_complaints = relationship(
        "Complaint",
        back_populates="customer",
        foreign_keys="Complaint.customer_id",
    )
    assigned_complaints = relationship(
        "Complaint",
        back_populates="assigned_agent",
        foreign_keys="Complaint.assigned_agent_id",
    )
    notifications = relationship("Notification", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"
