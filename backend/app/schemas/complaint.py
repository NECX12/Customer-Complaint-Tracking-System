"""Pydantic schemas for complaints, status updates, assignment, and history."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class ComplaintCreate(BaseModel):
    """Customer submits a new complaint."""
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    priority: str = Field(
        default="MEDIUM",
        pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$",
    )


class ComplaintResponse(BaseModel):
    """Full complaint representation returned by the API."""
    id: uuid.UUID
    customer_id: uuid.UUID
    assigned_agent_id: Optional[uuid.UUID] = None
    title: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    customer: Optional[UserResponse] = None
    assigned_agent: Optional[UserResponse] = None

    model_config = {"from_attributes": True}


class ComplaintListResponse(BaseModel):
    """Simplified complaint for list views (no nested relationships)."""
    id: uuid.UUID
    title: str
    status: str
    priority: str
    assigned_agent_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusUpdateRequest(BaseModel):
    """Agent updates complaint status."""
    status: str = Field(
        ...,
        pattern="^(IN_PROGRESS|RESOLVED|CLOSED)$",
        description="Target status",
    )
    comment: Optional[str] = Field(None, max_length=2000)


class AssignRequest(BaseModel):
    """Admin assigns a complaint to an agent."""
    agent_id: uuid.UUID
    comment: Optional[str] = Field(None, max_length=2000)


class StatusHistoryResponse(BaseModel):
    """Single entry in the complaint status timeline."""
    id: uuid.UUID
    old_status: Optional[str] = None
    new_status: str
    changed_by: UserResponse
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
