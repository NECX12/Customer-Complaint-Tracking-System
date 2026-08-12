"""
Authentication endpoints: register, login, and current user profile.

- POST /auth/register — customer self-registration
- POST /auth/login    — email/password login, returns JWT
- GET  /auth/me       — current user profile (requires valid token)

Design decision: login uses OAuth2PasswordRequestForm to be compatible with
FastAPI's built-in Swagger "Authorize" button, but the actual login logic
accepts email (not username). The form field is named "username" per the
OAuth2 spec, but we treat it as an email.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer account",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new CUSTOMER account.
    Agents and admins are created by administrators via /users.
    """
    try:
        user = auth_service.register_customer(
            db=db,
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate with email and password, receive a JWT access token.

    The 'username' field in the form should contain the email address
    (OAuth2 spec requires this field name).
    """
    user = auth_service.authenticate_user(
        db=db,
        email=form_data.username,  # OAuth2 form uses "username" field
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_service.create_token_for_user(user)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user
