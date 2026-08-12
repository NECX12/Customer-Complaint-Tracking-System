"""
Test fixtures — provides a test database, client, and auth helpers.

Uses an in-memory SQLite database for fast, isolated test execution
without requiring a running PostgreSQL instance. This is a pragmatic
trade-off: SQLite doesn't support all PostgreSQL features, but it's
sufficient for testing business logic and API behavior.

For full integration tests against PostgreSQL, set TEST_DATABASE_URL
in the environment.
"""

import os
import uuid
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password, create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.main import app

# Use SQLite for tests (fast, no external dependencies)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test.db"
)

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in TEST_DATABASE_URL else None,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency for tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator:
    """Provide a database session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    """Provide a FastAPI test client."""
    return TestClient(app)


# ── User factory helpers ─────────────────────────────────────────


def create_test_user(
    db,
    email: str = "test@example.com",
    name: str = "Test User",
    password: str = "testpass123",
    role: UserRole = UserRole.CUSTOMER,
) -> User:
    """Create a user in the test database."""
    user = User(
        id=uuid.uuid4(),
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_auth_headers(user: User) -> dict:
    """Generate Authorization headers for a test user."""
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer(db) -> User:
    return create_test_user(db, email="customer@test.com", role=UserRole.CUSTOMER)


@pytest.fixture
def agent(db) -> User:
    return create_test_user(
        db, email="agent@test.com", name="Test Agent", role=UserRole.AGENT
    )


@pytest.fixture
def admin(db) -> User:
    return create_test_user(
        db, email="admin@test.com", name="Test Admin", role=UserRole.ADMIN
    )
