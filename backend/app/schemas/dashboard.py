"""Pydantic schemas for role-specific dashboards."""

import uuid
from typing import Optional

from pydantic import BaseModel

from app.schemas.complaint import ComplaintListResponse
from app.schemas.user import UserResponse


class CustomerDashboard(BaseModel):
    """Customer dashboard: their complaint summary."""
    total_complaints: int
    open_complaints: int
    resolved_complaints: int
    recent_complaints: list[ComplaintListResponse]


class AgentDashboard(BaseModel):
    """Agent dashboard: assigned complaint workload."""
    total_assigned: int
    pending: int
    in_progress: int
    resolved: int
    recent_assignments: list[ComplaintListResponse]


class AgentPerformance(BaseModel):
    """Single agent's performance metrics for the admin dashboard."""
    agent: UserResponse
    total_assigned: int
    total_resolved: int
    total_open: int
    resolution_rate: float
    avg_resolution_hours: Optional[float] = None


class AdminDashboard(BaseModel):
    """System-wide dashboard for administrators."""
    total_complaints: int
    submitted: int
    assigned: int
    in_progress: int
    resolved: int
    closed: int
    unassigned: int
    total_agents: int
    active_agents: int
    agent_performance: list[AgentPerformance]
