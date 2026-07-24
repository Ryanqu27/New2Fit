"""
conftest.py — Shared pytest fixtures for New2Fit backend tests.

Key design decisions:
  - DATABASE_URL is overridden to an in-memory SQLite DB *before* any app
    module is imported. This is done at module level so the env var is set
    before database.py reads it.
  - All tables are created once per test session. Each test function gets its
    own DB session that is rolled back after the test, keeping tests isolated.
  - The FastAPI dependency `get_db` is overridden so the TestClient uses the
    same transactional session as the test, not the production DB.
  - `auth_client` is a factory fixture: call it with a user_id to get a
    TestClient with a valid JWT cookie pre-baked in (no real login needed).
"""

import os
# Must be set BEFORE importing anything from the app
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")

# ---------------------------------------------------------------------------
# Patch sqlalchemy.create_engine BEFORE importing database.py
#
# database.py creates its engine at module load time using PostgreSQL-specific
# pool arguments (pool_pre_ping, pool_recycle, pool_timeout) that SQLite's
# SingletonThreadPool does not accept. We intercept the call and strip those
# args when the URL is a SQLite URL.
# ---------------------------------------------------------------------------
import sqlalchemy as _sa
from sqlalchemy import create_engine as _real_create_engine

def _sqlite_safe_create_engine(url, **kwargs):
    if str(url).startswith("sqlite"):
        for key in ("pool_pre_ping", "pool_recycle", "pool_timeout"):
            kwargs.pop(key, None)
        kwargs.setdefault("connect_args", {"check_same_thread": False})
    return _real_create_engine(url, **kwargs)

# Replacing the attribute in the sqlalchemy namespace means that when database.py
# runs `from sqlalchemy import create_engine` it picks up our patched version.
_sa.create_engine = _sqlite_safe_create_engine

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from Users.auth import create_access_token
from limiter import limiter

# Disable rate limiting for the test session so we don't get 429s when spamming auth endpoints
limiter.enabled = False


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create a single in-memory SQLite engine for the entire test session."""
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(engine):
    """
    Provide a transactional DB session per test.
    Changes are rolled back after each test so tests don't bleed into each other.
    """
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# TestClient fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(db_session):
    """Unauthenticated TestClient with the DB dependency overridden."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_client(db_session):
    """
    Factory fixture. Returns a function that accepts a user_id and produces
    a TestClient with a valid JWT access_token cookie pre-set.

    Usage:
        def test_something(auth_client):
            c = auth_client(user_id=1)
            response = c.get("/api/workouts")
    """
    def _make_client(user_id: int) -> TestClient:
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        token = create_access_token(user_id)
        client = TestClient(app, raise_server_exceptions=True)
        client.cookies.set("access_token", token)
        return client

    yield _make_client
    app.dependency_overrides.clear()
