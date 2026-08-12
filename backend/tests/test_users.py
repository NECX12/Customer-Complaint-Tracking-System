"""
User management tests — admin operations.
"""

from tests.conftest import get_auth_headers


class TestUserManagement:
    """Admin user creation and management tests."""

    def test_admin_creates_agent(self, client, admin):
        headers = get_auth_headers(admin)
        response = client.post("/api/v1/users", headers=headers, json={
            "name": "New Agent",
            "email": "newagent@example.com",
            "password": "agent123",
            "role": "AGENT",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "AGENT"
        assert data["email"] == "newagent@example.com"

    def test_admin_creates_admin(self, client, admin):
        headers = get_auth_headers(admin)
        response = client.post("/api/v1/users", headers=headers, json={
            "name": "New Admin",
            "email": "newadmin@example.com",
            "password": "admin123",
            "role": "ADMIN",
        })
        assert response.status_code == 201
        assert response.json()["role"] == "ADMIN"

    def test_cannot_create_customer_via_admin(self, client, admin):
        """Customers are created via /auth/register, not /users."""
        headers = get_auth_headers(admin)
        response = client.post("/api/v1/users", headers=headers, json={
            "name": "Customer Via Admin",
            "email": "badcustomer@example.com",
            "password": "pass123",
            "role": "CUSTOMER",
        })
        assert response.status_code == 422  # Pydantic rejects CUSTOMER role

    def test_admin_lists_agents(self, client, admin, agent):
        headers = get_auth_headers(admin)
        response = client.get("/api/v1/users/agents", headers=headers)
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 1
        assert all(a["role"] == "AGENT" for a in agents)

    def test_admin_deactivates_user(self, client, db, admin, agent):
        headers = get_auth_headers(admin)
        response = client.put(
            f"/api/v1/users/{agent.id}",
            headers=headers,
            json={"is_active": False},
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False
