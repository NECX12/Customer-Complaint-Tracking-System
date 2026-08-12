"""
Authentication tests — registration, login, token validation.
"""

from tests.conftest import create_test_user, get_auth_headers
from app.db.models.user import UserRole


class TestRegistration:
    """Customer self-registration tests."""

    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json={
            "name": "New Customer",
            "email": "new@example.com",
            "password": "password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["role"] == "CUSTOMER"

    def test_register_duplicate_email(self, client, db):
        create_test_user(db, email="taken@example.com")
        response = client.post("/api/v1/auth/register", json={
            "name": "Another User",
            "email": "taken@example.com",
            "password": "password123",
        })
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        response = client.post("/api/v1/auth/register", json={
            "name": "Bad Email",
            "email": "not-an-email",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/api/v1/auth/register", json={
            "name": "Short Pass",
            "email": "short@example.com",
            "password": "12345",
        })
        assert response.status_code == 422


class TestLogin:
    """Login and token tests."""

    def test_login_success(self, client, db):
        create_test_user(db, email="login@example.com", password="mypassword")
        response = client.post("/api/v1/auth/login", data={
            "username": "login@example.com",
            "password": "mypassword",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, db):
        create_test_user(db, email="wrong@example.com", password="correctpass")
        response = client.post("/api/v1/auth/login", data={
            "username": "wrong@example.com",
            "password": "wrongpass",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/v1/auth/login", data={
            "username": "ghost@example.com",
            "password": "anypass",
        })
        assert response.status_code == 401


class TestCurrentUser:
    """GET /auth/me tests."""

    def test_get_me_authenticated(self, client, customer):
        headers = get_auth_headers(customer)
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == customer.email

    def test_get_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401
