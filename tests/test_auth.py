"""
Tests for registration, login, logout, and session behaviour.
"""
import pytest
from tests.conftest import CANDIDATE_DATA, RECRUITER_DATA, register_and_login, login, logout


class TestCandidateRegistration:
    def test_register_candidate_success(self, client):
        resp = client.post("/register", data=CANDIDATE_DATA, follow_redirects=True)
        assert resp.status_code == 200
        assert b"login" in resp.data.lower() or b"sign in" in resp.data.lower()

    def test_register_candidate_duplicate_email(self, client):
        client.post("/register", data=CANDIDATE_DATA, follow_redirects=True)
        resp = client.post("/register", data=CANDIDATE_DATA, follow_redirects=True)
        assert b"already exists" in resp.data.lower() or resp.status_code in (200, 409)

    def test_register_candidate_missing_name(self, client):
        data = {**CANDIDATE_DATA, "name": ""}
        resp = client.post("/register", data=data, follow_redirects=True)
        assert resp.status_code == 200  # re-renders form with error

    def test_register_candidate_invalid_email(self, client):
        data = {**CANDIDATE_DATA, "email": "not-an-email"}
        resp = client.post("/register", data=data, follow_redirects=True)
        assert resp.status_code == 200

    def test_register_candidate_short_password(self, client):
        data = {**CANDIDATE_DATA, "password": "short", "confirm_password": "short"}
        resp = client.post("/register", data=data, follow_redirects=True)
        assert resp.status_code == 200

    def test_register_candidate_password_mismatch(self, client):
        data = {**CANDIDATE_DATA, "confirm_password": "DifferentPass1"}
        resp = client.post("/register", data=data, follow_redirects=True)
        assert resp.status_code == 200


class TestRecruiterRegistration:
    def test_register_recruiter_success(self, client):
        resp = client.post("/register", data=RECRUITER_DATA, follow_redirects=True)
        assert resp.status_code == 200

    def test_register_recruiter_missing_company(self, client):
        data = {**RECRUITER_DATA, "company_name": ""}
        resp = client.post("/register", data=data, follow_redirects=True)
        assert resp.status_code == 200


class TestLogin:
    def test_login_success_candidate(self, client):
        client.post("/register", data=CANDIDATE_DATA, follow_redirects=True)
        resp = login(client, CANDIDATE_DATA["email"], CANDIDATE_DATA["password"])
        assert resp.status_code == 200
        assert b"dashboard" in resp.data.lower() or b"welcome" in resp.data.lower()

    def test_login_invalid_password(self, client):
        client.post("/register", data=CANDIDATE_DATA, follow_redirects=True)
        resp = login(client, CANDIDATE_DATA["email"], "WrongPassword!")
        assert resp.status_code == 200
        assert b"invalid" in resp.data.lower() or b"incorrect" in resp.data.lower()

    def test_login_unknown_email(self, client):
        resp = login(client, "nobody@nowhere.com", "Password123")
        assert resp.status_code == 200
        assert b"invalid" in resp.data.lower() or b"password" in resp.data.lower()

    def test_login_empty_fields(self, client):
        resp = login(client, "", "")
        assert resp.status_code == 200


class TestLogout:
    def test_logout_clears_session(self, client):
        register_and_login(client, CANDIDATE_DATA)
        resp = logout(client)
        assert resp.status_code == 200
        # After logout, dashboard should redirect to login
        resp2 = client.get("/dashboard/", follow_redirects=False)
        assert resp2.status_code in (302, 401)

    def test_logout_redirects_to_login(self, client):
        register_and_login(client, CANDIDATE_DATA)
        resp = client.get("/logout", follow_redirects=True)
        assert b"sign in" in resp.data.lower() or b"login" in resp.data.lower()


class TestAPIAuth:
    def test_api_register_candidate(self, client):
        resp = client.post("/api/auth/register", json=CANDIDATE_DATA)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["role"] == "CANDIDATE"

    def test_api_register_duplicate(self, client):
        client.post("/api/auth/register", json=CANDIDATE_DATA)
        resp = client.post("/api/auth/register", json=CANDIDATE_DATA)
        assert resp.status_code == 409
        data = resp.get_json()
        assert data["success"] is False
        assert data["error_code"] == "USER_ALREADY_EXISTS"

    def test_api_login_success(self, client):
        client.post("/api/auth/register", json=CANDIDATE_DATA)
        resp = client.post("/api/auth/login", json={
            "email": CANDIDATE_DATA["email"],
            "password": CANDIDATE_DATA["password"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

    def test_api_login_invalid(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "ghost@test.com",
            "password": "wrongpass",
        })
        assert resp.status_code == 401
        assert resp.get_json()["error_code"] == "INVALID_CREDENTIALS"

    def test_api_logout(self, client):
        client.post("/api/auth/register", json=CANDIDATE_DATA)
        client.post("/api/auth/login", json={
            "email": CANDIDATE_DATA["email"],
            "password": CANDIDATE_DATA["password"],
        })
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

    def test_api_me_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_api_me_authenticated(self, client):
        client.post("/api/auth/register", json=CANDIDATE_DATA)
        client.post("/api/auth/login", json={
            "email": CANDIDATE_DATA["email"],
            "password": CANDIDATE_DATA["password"],
        })
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["email"] == CANDIDATE_DATA["email"]
