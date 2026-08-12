"""Pydantic schemas for authentication requests and responses."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login credentials — used with OAuth2PasswordRequestForm as well."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Customer self-registration payload."""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    """JWT token response returned after successful login."""
    access_token: str
    token_type: str = "bearer"
