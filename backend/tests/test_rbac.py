"""
RBAC tests — verifies that role-based access control works correctly.

These tests ensure that:
- Customers cannot access admin/agent endpoints
- Agents cannot access admin endpoints
- Customers cannot view other customers' complaints
- Agents cannot modify unassigned complaints
"""

from tests.conftest import create_test_user, get_auth_headers
from app.db.models.user import UserRole
from app.db.models.complaint import Complaint, ComplaintStatus, ComplaintPriority


class TestCustomerRBAC:
    """Customers should NOT access admin or agent resources."""

    def test_customer_cannot_list_users(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.get("/api/v1/users", headers=headers)
        assert response.status_code == 403

    def test_customer_cannot_create_user(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.post("/api/v1/users", headers=headers, json={
            "name": "Hacker",
            "email": "hacker@example.com",
            "password": "hack123",
            "role": "ADMIN",
        })
        assert response.status_code == 403

    def test_customer_cannot_access_admin_dashboard(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.get("/api/v1/dashboard/admin", headers=headers)
        assert response.status_code == 403

    def test_customer_cannot_access_agent_dashboard(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.get("/api/v1/dashboard/agent", headers=headers)
        assert response.status_code == 403


class TestAgentRBAC:
    """Agents should NOT access admin resources."""

    def test_agent_cannot_list_users(self, client, agent):
        headers = get_auth_headers(agent)
        response = client.get("/api/v1/users", headers=headers)
        assert response.status_code == 403

    def test_agent_cannot_create_user(self, client, agent):
        headers = get_auth_headers(agent)
        response = client.post("/api/v1/users", headers=headers, json={
            "name": "Rogue",
            "email": "rogue@example.com",
            "password": "rogue123",
            "role": "ADMIN",
        })
        assert response.status_code == 403

    def test_agent_cannot_access_admin_dashboard(self, client, agent):
        headers = get_auth_headers(agent)
        response = client.get("/api/v1/dashboard/admin", headers=headers)
        assert response.status_code == 403

    def test_agent_cannot_assign_complaints(self, client, db, agent, customer):
        # Create a complaint
        complaint = Complaint(
            customer_id=customer.id,
            title="Test complaint",
            description="Test description here",
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        headers = get_auth_headers(agent)
        response = client.post(
            f"/api/v1/complaints/{complaint.id}/assign",
            headers=headers,
            json={"agent_id": str(agent.id)},
        )
        assert response.status_code == 403


class TestComplaintOwnership:
    """Users should only access complaints they own or are assigned to."""

    def test_customer_cannot_see_other_customers_complaint(self, client, db):
        customer1 = create_test_user(db, email="c1@test.com", role=UserRole.CUSTOMER)
        customer2 = create_test_user(db, email="c2@test.com", role=UserRole.CUSTOMER)

        complaint = Complaint(
            customer_id=customer1.id,
            title="Private complaint",
            description="This is private information",
            status=ComplaintStatus.SUBMITTED,
            priority=ComplaintPriority.MEDIUM,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        # Customer 2 tries to view customer 1's complaint
        headers = get_auth_headers(customer2)
        response = client.get(
            f"/api/v1/complaints/{complaint.id}",
            headers=headers,
        )
        assert response.status_code == 403

    def test_agent_cannot_update_unassigned_complaint(self, client, db, agent, customer):
        # Create a complaint assigned to a different agent
        other_agent = create_test_user(
            db, email="other@test.com", name="Other Agent", role=UserRole.AGENT
        )
        complaint = Complaint(
            customer_id=customer.id,
            assigned_agent_id=other_agent.id,
            title="Not my complaint",
            description="Assigned to someone else",
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
            json={"status": "IN_PROGRESS"},
        )
        assert response.status_code == 403
