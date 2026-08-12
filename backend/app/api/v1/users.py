"""
User management endpoints — admin-only operations.

- GET  /users        — list all users (with optional role filter)
- POST /users        — create an AGENT or ADMIN account
- GET  /users/agents — list active agents (for assignment dropdown)
- PUT  /users/{id}   — update user (name, active status)
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse
from app.services import audit_service, user_service

router = APIRouter()


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List all users",
)
def list_users(
    role: str = Query(None, description="Filter by role: CUSTOMER, AGENT, ADMIN"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """List all users, optionally filtered by role."""
    return user_service.get_all_users(db, role_filter=role)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an agent or admin account",
)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Admin creates a new AGENT or ADMIN account.
    Customer accounts are created via /auth/register.
    """
    try:
        user = user_service.create_user(
            db=db,
            name=payload.name,
            email=payload.email,
            password=payload.password,
            role=payload.role,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    # Audit log
    action = "ADMIN_CREATED_AGENT" if payload.role == "AGENT" else "ADMIN_CREATED_ADMIN"
    audit_service.log_action(
        db=db,
        actor_id=current_user.id,
        action=action,
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email, "role": user.role.value},
    )

    return user


@router.get(
    "/agents",
    response_model=list[UserResponse],
    summary="List active agents",
)
def list_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """List all active agents — used for the complaint assignment dropdown."""
    return user_service.get_agents(db)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
)
def update_user(
    user_id: uuid.UUID,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Update user fields (name, active status)."""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = user_service.update_user(
        db=db,
        user=user,
        name=payload.name,
        is_active=payload.is_active,
    )
    return updated
