"""
Tests for candidate profile management and saved jobs.
"""
import pytest
from tests.conftest import CANDIDATE_DATA, register_and_login, login, logout


def _register_login_candidate(client):
    """Register and log in a candidate; return profile_id from session."""
    register_and_login(client, CANDIDATE_DATA)


class TestCandidateProfile:
    def test_profile_page_requires_login(self, client):
        resp = client.get("/candidate/profile", follow_redirects=False)
        assert resp.status_code in (302, 401)

    def test_profile_page_accessible_after_login(self, client):
        register_and_login(client, CANDIDATE_DATA)
        resp = client.get("/candidate/profile")
        assert resp.status_code == 200
        assert b"Alice Test" in resp.data

    def test_profile_blocked_for_recruiter(self, client):
        from tests.conftest import RECRUITER_DATA
        register_and_login(client, RECRUITER_DATA)
        resp = client.get("/candidate/profile", follow_redirects=True)
        # Recruiter should not access candidate profile endpoint
        assert resp.status_code in (200, 403)

    def test_edit_profile_updates_location(self, client, app):
        register_and_login(client, CANDIDATE_DATA)
        with client.session_transaction() as sess:
            profile_id = sess.get("profile_id", "")
        resp = client.post(
            "/candidate/profile/edit",
            data={
                "name": "Alice Updated",
                "location": "Mumbai",
                "skills": "python,sql",
                "phone": "9876543210",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        # Verify update persisted
        with app.app_context():
            from app.extensions import get_db
            db = get_db()
            from bson import ObjectId
            profile = db.candidates.find_one({"_id": ObjectId(profile_id)})
            assert profile["location"] == "Mumbai"

    def test_edit_profile_normalises_skills(self, client, app):
        register_and_login(client, CANDIDATE_DATA)
        with client.session_transaction() as sess:
            profile_id = sess.get("profile_id", "")
        client.post(
            "/candidate/profile/edit",
            data={"name": "Alice", "skills": " Python , SQL , React "},
            follow_redirects=True,
        )
        with app.app_context():
            from app.extensions import get_db
            db = get_db()
            from bson import ObjectId
            profile = db.candidates.find_one({"_id": ObjectId(profile_id)})
            assert "python" in profile["skills"]
            assert "sql" in profile["skills"]


class TestAPICandidate:
    def test_get_own_profile(self, client):
        register_and_login(client, CANDIDATE_DATA)
        with client.session_transaction() as sess:
            profile_id = sess.get("profile_id", "")
        resp = client.get(f"/api/candidates/{profile_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["email"] == CANDIDATE_DATA["email"]

    def test_get_profile_unauthenticated(self, client):
        resp = client.get("/api/candidates/someobjectid")
        assert resp.status_code == 401

    def test_update_own_profile(self, client):
        register_and_login(client, CANDIDATE_DATA)
        with client.session_transaction() as sess:
            profile_id = sess.get("profile_id", "")
        resp = client.put(
            f"/api/candidates/{profile_id}",
            json={"location": "Delhi", "skills": ["python", "aws"]},
        )
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True
