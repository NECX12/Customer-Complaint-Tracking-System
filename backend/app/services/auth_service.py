"""
Authentication service — registration and login logic.

Keeps route handlers thin by encapsulating the business logic for:
- Customer self-registration (validates uniqueness, hashes password)
- Login (validates credentials, issues JWT)
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.db.models.user import User, UserRole

logger = logging.getLogger(__name__)


def register_customer(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> User:
    """
    Register a new customer account.

    Raises ValueError if the email is already taken.
    Only customers can self-register — agents and admins are created by admins.
    """
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Email already registered")

    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"Customer registered: {email}")
    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Validate login credentials.

    Returns the User if credentials are valid, None otherwise.
    Never reveals whether the email or the password was wrong.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_token_for_user(user: User) -> str:
    """Create a JWT access token for an authenticated user."""
    return create_access_token(
        subject=str(user.id),
        role=user.role.value,
    )
