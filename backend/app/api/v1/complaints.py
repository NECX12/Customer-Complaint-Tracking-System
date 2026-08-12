"""
Complaint endpoints — CRUD, status updates, assignment, and history.

Authorization logic:
- Customers see only their own complaints
- Agents see only their assigned complaints
- Admins see all complaints
- Status updates enforce the state machine (VALID_TRANSITIONS)
- Assignment is admin-only
- History is available to authorized viewers of the complaint

Route handlers are kept thin — business logic lives in complaint_service.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.complaint import (
    AssignRequest,
    ComplaintCreate,
    ComplaintListResponse,
    ComplaintResponse,
    StatusHistoryResponse,
    StatusUpdateRequest,
)
from app.schemas.user import UserResponse
from app.services import audit_service, complaint_service, notification_service, user_service

router = APIRouter()


@router.post(
    "",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new complaint",
)
def create_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
):
    """
    Customer submits a new complaint.
    The customer_id is set from the JWT — never from user input.
    """
    complaint = complaint_service.create_complaint(
        db=db,
        customer=current_user,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
    )

    # Queue notification asynchronously
    notification_service.notify_complaint_submitted(
        db=db,
        customer_id=current_user.id,
        complaint_id=complaint.id,
        title=complaint.title,
    )

    return complaint


@router.get(
    "",
    response_model=list[ComplaintListResponse],
    summary="List complaints",
)
def list_complaints(
    status_filter: str = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List complaints based on the user's role:
    - CUSTOMER: their own complaints
    - AGENT: their assigned complaints
    - ADMIN: all complaints (with optional status filter)
    """
    if current_user.role == UserRole.CUSTOMER:
        complaints = complaint_service.get_complaints_by_customer(db, current_user.id)
    elif current_user.role == UserRole.AGENT:
        complaints = complaint_service.get_complaints_by_agent(db, current_user.id)
    else:  # ADMIN
        complaints = complaint_service.get_all_complaints(db, status_filter)

    return complaints


@router.get(
    "/{complaint_id}",
    response_model=ComplaintResponse,
    summary="Get complaint details",
)
def get_complaint(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed complaint information.
    Enforces ownership: customers can only see their own, agents only their assigned.
    """
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Authorization: check access based on role
    _authorize_complaint_access(complaint, current_user)

    return complaint


@router.put(
    "/{complaint_id}/status",
    response_model=ComplaintResponse,
    summary="Update complaint status",
)
def update_status(
    complaint_id: uuid.UUID,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGENT, UserRole.ADMIN)),
):
    """
    Update complaint status — validates state machine transitions.
    Agents can only update their assigned complaints.
    """
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Agents can only modify their assigned complaints
    if current_user.role == UserRole.AGENT:
        if complaint.assigned_agent_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to you")

    old_status = complaint.status.value

    try:
        complaint = complaint_service.update_complaint_status(
            db=db,
            complaint=complaint,
            new_status_str=payload.status,
            changed_by=current_user,
            comment=payload.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Notify the customer about the status change
    if payload.status == "RESOLVED":
        notification_service.notify_complaint_resolved(
            db=db,
            customer_id=complaint.customer_id,
            complaint_id=complaint.id,
            title=complaint.title,
        )
    else:
        notification_service.notify_status_updated(
            db=db,
            customer_id=complaint.customer_id,
            complaint_id=complaint.id,
            title=complaint.title,
            old_status=old_status,
            new_status=payload.status,
        )

    return complaint


@router.post(
    "/{complaint_id}/assign",
    response_model=ComplaintResponse,
    summary="Assign complaint to an agent",
)
def assign_complaint(
    complaint_id: uuid.UUID,
    payload: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Admin assigns (or reassigns) a complaint to an agent.
    Validates that the target is an active AGENT.
    """
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    agent = user_service.get_user_by_id(db, payload.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        complaint = complaint_service.assign_complaint(
            db=db,
            complaint=complaint,
            agent=agent,
            assigned_by=current_user,
            comment=payload.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Audit log
    audit_service.log_action(
        db=db,
        actor_id=current_user.id,
        action="COMPLAINT_ASSIGNED",
        entity_type="complaint",
        entity_id=complaint.id,
        details={"agent_id": str(agent.id), "agent_email": agent.email},
    )

    # Notify the assigned agent
    notification_service.notify_complaint_assigned(
        db=db,
        agent_id=agent.id,
        complaint_id=complaint.id,
        title=complaint.title,
        agent_name=agent.name,
    )

    return complaint


@router.get(
    "/{complaint_id}/history",
    response_model=list[StatusHistoryResponse],
    summary="Get complaint status history",
)
def get_history(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the full status transition timeline for a complaint.
    Used by the frontend to render the complaint timeline component.
    """
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    _authorize_complaint_access(complaint, current_user)

    history = complaint_service.get_complaint_history(db, complaint_id)

    # Manually build the response to include the actor details
    return [
        StatusHistoryResponse(
            id=h.id,
            old_status=h.old_status,
            new_status=h.new_status,
            changed_by=UserResponse.model_validate(h.actor),
            comment=h.comment,
            created_at=h.created_at,
        )
        for h in history
    ]


def _authorize_complaint_access(complaint, current_user: User) -> None:
    """
    Check that the current user is authorized to view this complaint.
    Raises 403 if not.

    - Customers can only see their own complaints
    - Agents can only see their assigned complaints
    - Admins can see everything
    """
    if current_user.role == UserRole.CUSTOMER:
        if complaint.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.AGENT:
        if complaint.assigned_agent_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to you")
    # Admins have unrestricted access
