"""
User management service — admin operations for creating and managing users.

Only admins can create AGENT and ADMIN accounts.
Customer accounts are created via self-registration (see auth_service).
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.user import User, UserRole

logger = logging.getLogger(__name__)


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str,
) -> User:
    """
    Create an AGENT or ADMIN account (admin-only operation).

    Raises ValueError if the email is already taken or the role is invalid.
    """
    if role not in (UserRole.AGENT.value, UserRole.ADMIN.value):
        raise ValueError("Can only create AGENT or ADMIN accounts")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Email already registered")

    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole(role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"{role} account created: {email}")
    return user


def get_all_users(
    db: Session,
    role_filter: Optional[str] = None,
) -> list[User]:
    """Get all users, optionally filtered by role."""
    query = db.query(User)
    if role_filter:
        query = query.filter(User.role == UserRole(role_filter))
    return query.order_by(User.created_at.desc()).all()


def get_agents(db: Session) -> list[User]:
    """Get all active agents — used for the assignment dropdown."""
    return (
        db.query(User)
        .filter(User.role == UserRole.AGENT, User.is_active == True)
        .order_by(User.name)
        .all()
    )


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Fetch a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def update_user(
    db: Session,
    user: User,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> User:
    """Update user fields (admin operation)."""
    if name is not None:
        user.name = name
    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)

    logger.info(f"User updated: {user.email}")
    return user
