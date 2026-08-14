"""
Dashboard service — aggregated statistics for each role's dashboard.

Each function performs the necessary SQL queries and returns a Pydantic schema
ready for the route handler to return. This keeps route handlers completely thin.

Design decision: These queries use SQLAlchemy ORM rather than raw SQL for
readability and safety.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.complaint import Complaint, ComplaintStatus
from app.db.models.user import User, UserRole
from app.schemas.complaint import ComplaintListResponse
from app.schemas.dashboard import (
    AdminDashboard,
    AgentDashboard,
    AgentPerformance,
    CustomerDashboard,
)
from app.schemas.user import UserResponse


def get_customer_dashboard(db: Session, customer_id: uuid.UUID) -> CustomerDashboard:
    """Build dashboard stats for a customer — their own complaints only."""
    base_query = db.query(Complaint).filter(Complaint.customer_id == customer_id)

    total = base_query.count()
    resolved = base_query.filter(
        Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
    ).count()
    open_count = total - resolved

    recent = (
        base_query
        .order_by(Complaint.created_at.desc())
        .limit(10)
        .all()
    )

    return CustomerDashboard(
        total_complaints=total,
        open_complaints=open_count,
        resolved_complaints=resolved,
        recent_complaints=[ComplaintListResponse.model_validate(c) for c in recent],
    )


def get_agent_dashboard(db: Session, agent_id: uuid.UUID) -> AgentDashboard:
    """Build dashboard stats for an agent — their assigned complaints."""
    base_query = db.query(Complaint).filter(Complaint.assigned_agent_id == agent_id)

    total = base_query.count()
    pending = base_query.filter(Complaint.status == ComplaintStatus.ASSIGNED).count()
    in_progress = base_query.filter(Complaint.status == ComplaintStatus.IN_PROGRESS).count()
    resolved = base_query.filter(
        Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
    ).count()

    recent = (
        base_query
        .order_by(Complaint.updated_at.desc())
        .limit(10)
        .all()
    )

    return AgentDashboard(
        total_assigned=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        recent_assignments=[ComplaintListResponse.model_validate(c) for c in recent],
    )


def get_admin_dashboard(db: Session) -> AdminDashboard:
    """Build system-wide dashboard stats with agent performance metrics."""
    # Complaint counts by status
    total = db.query(Complaint).count()
    submitted = db.query(Complaint).filter(Complaint.status == ComplaintStatus.SUBMITTED).count()
    assigned = db.query(Complaint).filter(Complaint.status == ComplaintStatus.ASSIGNED).count()
    in_progress = db.query(Complaint).filter(Complaint.status == ComplaintStatus.IN_PROGRESS).count()
    resolved = db.query(Complaint).filter(Complaint.status == ComplaintStatus.RESOLVED).count()
    closed = db.query(Complaint).filter(Complaint.status == ComplaintStatus.CLOSED).count()
    unassigned = db.query(Complaint).filter(Complaint.assigned_agent_id.is_(None)).count()

    # Agent counts
    total_agents = db.query(User).filter(User.role == UserRole.AGENT).count()
    active_agents = db.query(User).filter(
        User.role == UserRole.AGENT, User.is_active == True
    ).count()

    # Agent performance
    agents = db.query(User).filter(User.role == UserRole.AGENT).all()
    agent_perf = []
    for agent in agents:
        agent_complaints = db.query(Complaint).filter(
            Complaint.assigned_agent_id == agent.id
        )
        a_total = agent_complaints.count()
        a_resolved = agent_complaints.filter(
            Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
        ).count()
        a_open = a_total - a_resolved

        # Resolution rate
        rate = (a_resolved / a_total * 100) if a_total > 0 else 0.0

        # Average resolution time (hours)
        avg_hours = None
        resolved_complaints = agent_complaints.filter(
            Complaint.resolved_at.isnot(None)
        ).all()
        if resolved_complaints:
            total_hours = sum(
                (c.resolved_at - c.created_at).total_seconds() / 3600
                for c in resolved_complaints
            )
            avg_hours = round(total_hours / len(resolved_complaints), 1)

        agent_perf.append(AgentPerformance(
            agent=UserResponse.model_validate(agent),
            total_assigned=a_total,
            total_resolved=a_resolved,
            total_open=a_open,
            resolution_rate=round(rate, 1),
            avg_resolution_hours=avg_hours,
        ))

    return AdminDashboard(
        total_complaints=total,
        submitted=submitted,
        assigned=assigned,
        in_progress=in_progress,
        resolved=resolved,
        closed=closed,
        unassigned=unassigned,
        total_agents=total_agents,
        active_agents=active_agents,
        agent_performance=agent_perf,
    )
