"""
Complaint lifecycle tests — creation, status transitions, assignment, history.
"""

import uuid

from tests.conftest import create_test_user, get_auth_headers
from app.db.models.user import UserRole
from app.db.models.complaint import Complaint, ComplaintStatus, ComplaintPriority


class TestComplaintCreation:
    """Complaint submission tests."""

    def test_customer_creates_complaint(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.post("/api/v1/complaints", headers=headers, json={
            "title": "My generator broke",
            "description": "It stopped working after 2 hours of operation",
            "priority": "HIGH",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "SUBMITTED"
        assert data["priority"] == "HIGH"
        assert data["customer_id"] == str(customer.id)

    def test_complaint_has_initial_status_submitted(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.post("/api/v1/complaints", headers=headers, json={
            "title": "Status test complaint",
            "description": "Testing initial status assignment",
        })
        assert response.json()["status"] == "SUBMITTED"

    def test_complaint_default_priority_is_medium(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.post("/api/v1/complaints", headers=headers, json={
            "title": "Priority test complaint",
            "description": "Testing default priority assignment",
        })
        assert response.json()["priority"] == "MEDIUM"

    def test_agent_cannot_submit_complaint(self, client, agent):
        headers = get_auth_headers(agent)
        response = client.post("/api/v1/complaints", headers=headers, json={
            "title": "Agent complaint",
            "description": "Agents should not submit complaints",
        })
        assert response.status_code == 403


class TestComplaintHistory:
    """Status history and timeline tests."""

    def test_creation_creates_history_entry(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.post("/api/v1/complaints", headers=headers, json={
            "title": "History test",
            "description": "Should create initial history entry",
        })
        complaint_id = response.json()["id"]

        history_response = client.get(
            f"/api/v1/complaints/{complaint_id}/history",
            headers=headers,
        )
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) == 1
        assert history[0]["old_status"] is None
        assert history[0]["new_status"] == "SUBMITTED"


class TestStatusTransitions:
    """State machine transition tests."""

    def test_agent_starts_work(self, client, db, agent, customer, admin):
        # Create and assign complaint
        complaint = Complaint(
            customer_id=customer.id,
            assigned_agent_id=agent.id,
            title="Transition test",
            description="Testing ASSIGNED -> IN_PROGRESS",
            status=ComplaintStatus.ASSIGNED,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        headers = get_auth_headers(agent)
        response = client.put(
            f"/api/v1/complaints/{complaint.id}/status",
            headers=headers,
            json={"status": "IN_PROGRESS", "comment": "Starting investigation"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"

    def test_agent_resolves_complaint(self, client, db, agent, customer):
        complaint = Complaint(
            customer_id=customer.id,
            assigned_agent_id=agent.id,
            title="Resolve test",
            description="Testing IN_PROGRESS -> RESOLVED",
            status=ComplaintStatus.IN_PROGRESS,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        headers = get_auth_headers(agent)
        response = client.put(
            f"/api/v1/complaints/{complaint.id}/status",
            headers=headers,
            json={"status": "RESOLVED", "comment": "Fixed the issue"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "RESOLVED"
        assert data["resolved_at"] is not None

    def test_invalid_transition_rejected(self, client, db, agent, customer):
        complaint = Complaint(
            customer_id=customer.id,
            assigned_agent_id=agent.id,
            title="Invalid transition",
            description="Testing ASSIGNED -> RESOLVED (skipping IN_PROGRESS)",
            status=ComplaintStatus.ASSIGNED,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        headers = get_auth_headers(agent)
        response = client.put(
            f"/api/v1/complaints/{complaint.id}/status",
            headers=headers,
            json={"status": "RESOLVED"},
        )
        assert response.status_code == 400


class TestComplaintAssignment:
    """Admin assignment tests."""

    def test_admin_assigns_complaint(self, client, db, admin, agent, customer):
        complaint = Complaint(
            customer_id=customer.id,
            title="Assignment test",
            description="Testing admin assignment",
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.HIGH,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        headers = get_auth_headers(admin)
        response = client.post(
            f"/api/v1/complaints/{complaint.id}/assign",
            headers=headers,
            json={"agent_id": str(agent.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_agent_id"] == str(agent.id)
        assert data["status"] == "ASSIGNED"

    def test_cannot_assign_to_non_agent(self, client, db, admin, customer):
        complaint = Complaint(
            customer_id=customer.id,
            title="Bad assignment",
            description="Should not assign to a customer",
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        headers = get_auth_headers(admin)
        response = client.post(
            f"/api/v1/complaints/{complaint.id}/assign",
            headers=headers,
            json={"agent_id": str(customer.id)},
        )
        assert response.status_code == 400

    def test_cannot_assign_to_inactive_agent(self, client, db, admin, customer):
        inactive_agent = create_test_user(
            db, email="inactive@test.com", name="Inactive", role=UserRole.AGENT
        )
        inactive_agent.is_active = False
        db.commit()

        complaint = Complaint(
            customer_id=customer.id,
            title="Inactive assignment",
            description="Should not assign to inactive agent",
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        headers = get_auth_headers(admin)
        response = client.post(
            f"/api/v1/complaints/{complaint.id}/assign",
            headers=headers,
            json={"agent_id": str(inactive_agent.id)},
        )
        assert response.status_code == 400
