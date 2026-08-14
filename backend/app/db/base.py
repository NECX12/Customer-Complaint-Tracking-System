"""
SQLAlchemy declarative base and reusable model mixins.

Design decision: We use a TimestampMixin rather than putting created_at/updated_at
on every model manually. This keeps models DRY and ensures consistent timestamp
behavior across all tables.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """
    Mixin that adds `created_at` and ``updated_at` columns to any model.

    - created_at: set automatically by the database on INSERT
    - updated_at: set automatically on INSERT and updated on every UPDATE
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
