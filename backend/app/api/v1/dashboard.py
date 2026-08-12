"""
Dashboard endpoints — role-specific statistics.

Each role gets its own dashboard endpoint with pre-aggregated data,
reducing frontend complexity and the number of API calls needed.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.dashboard import AdminDashboard, AgentDashboard, CustomerDashboard
from app.services import dashboard_service

router = APIRouter()


@router.get(
    "/customer",
    response_model=CustomerDashboard,
    summary="Customer dashboard statistics",
)
def customer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CUSTOMER)),
):
    """Get complaint statistics for the authenticated customer."""
    return dashboard_service.get_customer_dashboard(db, current_user.id)


@router.get(
    "/agent",
    response_model=AgentDashboard,
    summary="Agent dashboard statistics",
)
def agent_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.AGENT)),
):
    """Get assigned complaint workload for the authenticated agent."""
    return dashboard_service.get_agent_dashboard(db, current_user.id)


@router.get(
    "/admin",
    response_model=AdminDashboard,
    summary="Admin dashboard statistics",
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Get system-wide statistics and agent performance metrics."""
    return dashboard_service.get_admin_dashboard(db)
