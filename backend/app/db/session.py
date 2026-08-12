"""
Database session configuration.

Creates the SQLAlchemy engine and session factory. The same engine works for both
local PostgreSQL (Docker) and Supabase PostgreSQL — only the DATABASE_URL differs.

Design decision: Synchronous SQLAlchemy was chosen over async because:
1. Simpler to understand and debug (important for interview defensibility).
2. Performance difference is negligible for this application's scale.
3. Async SQLAlchemy can be discussed as a future optimization.

pool_pre_ping=True is enabled to handle Supabase connection drops gracefully —
the pool verifies each connection is alive before using it.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    The session is automatically closed after the request completes,
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
