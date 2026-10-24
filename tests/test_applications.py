"""
Tests for job applications: submit, duplicate prevention, status transitions, withdrawal.
"""
import pytest
from tests.conftest import CANDIDATE_DATA, RECRUITER_DATA, JOB_DATA, register_and_login, login, logout


def _setup_recruiter_and_job(client):
    """Register recruiter and create a job; return (job_id, recruiter session logout)."""
    register_and_login(client, RECRUITER_DATA)
    resp = client.post("/api/jobs", json=JOB_DATA)
    job_id = resp.get_json()["data"]["_id"]
    logout(client)
    return job_id


def _setup_candidate(client):
    register_and_login(client, CANDIDATE_DATA)
    with client.session_transaction() as sess:
        return sess.get("profile_id", "")


class TestApplicationSubmit:
    def test_apply_requires_login(self, client):
        register_and_login(client, RECRUITER_DATA)
        resp = client.post("/api/jobs", json=JOB_DATA)
        job_id = resp.get_json()["data"]["_id"]
        logout(client)
        resp = client.post(f"/api/jobs/{job_id}/apply")
        assert resp.status_code == 401

    def test_apply_success(self, client):
        job_id = _setup_recruiter_and_job(client)
        _setup_candidate(client)
        resp = client.post(f"/api/jobs/{job_id}/apply")
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "APPLIED"

    def test_apply_to_nonexistent_job(self, client):
        _setup_candidate(client)
        resp = client.post("/api/jobs/000000000000000000000000/apply")
        assert resp.status_code == 404
        assert resp.get_json()["error_code"] == "JOB_NOT_FOUND"


class TestDuplicateApplication:
    def test_duplicate_application_rejected(self, client):
        job_id = _setup_recruiter_and_job(client)
        _setup_candidate(client)
        client.post(f"/api/jobs/{job_id}/apply")
        resp = client.post(f"/api/jobs/{job_id}/apply")
        assert resp.status_code == 409
        assert resp.get_json()["error_code"] == "DUPLICATE_APPLICATION"


class TestApplicationStatus:
    def _apply_and_get_app_id(self, client):
        job_id = _setup_recruiter_and_job(client)
        _setup_candidate(client)
        resp = client.post(f"/api/jobs/{job_id}/apply")
        return resp.get_json()["data"]["_id"], job_id

    def test_recruiter_can_update_status_to_shortlisted(self, client):
        app_id, job_id = self._apply_and_get_app_id(client)
        logout(client)
        login(client, RECRUITER_DATA["email"], RECRUITER_DATA["password"])
        resp = client.put(f"/api/applications/{app_id}/status", json={"status": "SHORTLISTED"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["status"] == "SHORTLISTED"

    def test_invalid_status_transition(self, client):
        app_id, _ = self._apply_and_get_app_id(client)
        logout(client)
        login(client, RECRUITER_DATA["email"], RECRUITER_DATA["password"])
        # Can't jump directly from APPLIED to SELECTED
        resp = client.put(f"/api/applications/{app_id}/status", json={"status": "SELECTED"})
        assert resp.status_code in (400, 422)

    def test_candidate_cannot_update_status(self, client):
        app_id, _ = self._apply_and_get_app_id(client)
        # Still logged in as candidate
        resp = client.put(f"/api/applications/{app_id}/status", json={"status": "SHORTLISTED"})
        assert resp.status_code == 403

    def test_list_applications_as_candidate(self, client):
        job_id = _setup_recruiter_and_job(client)
        _setup_candidate(client)
        client.post(f"/api/jobs/{job_id}/apply")
        resp = client.get("/api/applications")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["total"] >= 1

    def test_application_withdrawal(self, client):
        job_id = _setup_recruiter_and_job(client)
        _setup_candidate(client)
        resp = client.post(f"/api/jobs/{job_id}/apply")
        app_id = resp.get_json()["data"]["_id"]
        # Withdraw via web route
        resp2 = client.post(f"/candidate/applications/{app_id}/withdraw", follow_redirects=True)
        assert resp2.status_code == 200

    def test_closed_job_rejects_application(self, client, app):
        job_id = _setup_recruiter_and_job(client)
        # Close the job directly in DB
        with app.app_context():
            from app.extensions import get_db
            from bson import ObjectId
            get_db().jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {"status": "CLOSED"}})
        _setup_candidate(client)
        resp = client.post(f"/api/jobs/{job_id}/apply")
        assert resp.status_code == 400
        assert resp.get_json()["error_code"] == "JOB_CLOSED"
