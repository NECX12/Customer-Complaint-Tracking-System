"""
FastAPI dependencies for authentication and role-based authorization.

Two key dependencies are provided:

1. get_current_user — extracts and validates the JWT from the Authorization header,
   fetches the user from the database, and raises 401/403 as appropriate.

2. require_role(*roles) — a factory that returns a dependency which additionally
   checks that the authenticated user has one of the specified roles.

Usage in route handlers:
    @router.get("/admin-only")
    def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uuid

from app.core.security import decode_access_token
from app.db.session import get_db
from app.db.models.user import User, UserRole

# tokenUrl tells Swagger UI where the login endpoint is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT, fetch the user, and validate they are active.

    Raises:
        401 — if the token is missing, invalid, expired, or user not found.
        403 — if the user account is deactivated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_value = payload.get("sub")
    if user_id_value is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(str(user_id_value))
    except (ValueError, AttributeError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


def require_role(*roles: UserRole):
    """
    Factory that creates a dependency requiring the user to have one of the
    specified roles.

    Example:
        require_role(UserRole.ADMIN)           — admin only
        require_role(UserRole.ADMIN, UserRole.AGENT) — admin or agent
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {[r.value for r in roles]}",
            )
        return current_user

    return role_checker
