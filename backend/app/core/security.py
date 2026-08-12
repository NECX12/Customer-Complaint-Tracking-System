"""
Security utilities: password hashing and JWT token management.

- Password hashing: passlib with bcrypt (industry standard, slow-by-design to resist brute force).
- JWT: python-jose with HS256 (symmetric signing — appropriate for a monolith where the same
  server issues and verifies tokens).

The JWT payload carries the user's ID and role so that the auth dependency can authorize
requests without hitting the database for role checks on every call.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt is deliberately slow — makes brute-force attacks impractical
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Payload:
      - sub:  user ID (UUID as string)
      - role: user role enum value (CUSTOMER / AGENT / ADMIN)
      - exp:  expiration timestamp
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Returns the payload dict on success, or None if the token is
    invalid, expired, or tampered with.
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None
