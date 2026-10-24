"""
Pytest configuration and shared fixtures for HireHub tests.
"""
import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import get_db


@pytest.fixture(scope="session")
def app():
    """Create the Flask application once per test session."""
    application = create_app(TestingConfig())
    yield application


@pytest.fixture(scope="session")
def _db_session(app):
    """
    Session-scoped database handle used only for teardown.
    Tests must not use this directly — use the `db` fixture instead.
    """
    with app.app_context():
        database = get_db()
        yield database
        # Final teardown: drop all test collections
        for col in database.list_collection_names():
            database.drop_collection(col)


@pytest.fixture(autouse=True)
def clean_collections(_db_session):
    """
    Wipe every collection before each test for full isolation.
    Runs automatically for every test function.
    """
    for col in _db_session.list_collection_names():
        _db_session[col].delete_many({})
    yield


@pytest.fixture
def db(app):
    """
    Function-scoped database handle for tests that need to inspect the DB directly.
    Uses the same underlying connection as `_db_session`.
    """
    with app.app_context():
        yield get_db()


@pytest.fixture
def client(app):
    """
    Function-scoped test client — each test gets a fresh client with no
    cookies or session state from previous tests.  This is the standard
    pytest-flask pattern and is required because session state (logged-in
    user, role, profile_id) must not leak between tests.
    """
    with app.test_client() as c:
        yield c


# ---------- reusable data helpers ----------

CANDIDATE_DATA = {
    "name": "Alice Test",
    "email": "alice@test.com",
    "phone": "9876543210",
    "password": "Password123",
    "confirm_password": "Password123",
    "role": "CANDIDATE",
}

RECRUITER_DATA = {
    "name": "Bob Recruiter",
    "email": "bob@recruiter.com",
    "phone": "9123456780",
    "password": "Password123",
    "confirm_password": "Password123",
    "company_name": "TestCorp",
    "role": "RECRUITER",
}

JOB_DATA = {
    "title": "Python Developer",
    "description": "Build backend services using Python and Flask.",
    "location": "Bangalore",
    "work_mode": "HYBRID",
    "employment_type": "FULL_TIME",
    "skills": "python,flask,mongodb",
    "experience_min": "1",
    "experience_max": "5",
    "salary_min": "8",
    "salary_max": "20",
}


def register_and_login(client, data: dict):
    """Register a user then log them in. Returns the login response."""
    client.post("/register", data=data, follow_redirects=True)
    return client.post(
        "/login",
        data={"email": data["email"], "password": data["password"]},
        follow_redirects=True,
    )


def login(client, email: str, password: str):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def logout(client):
    return client.get("/logout", follow_redirects=True)
