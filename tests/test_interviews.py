"""
Tests for interview scheduling, update, and cancellation.
"""
import pytest
from tests.conftest import CANDIDATE_DATA, RECRUITER_DATA, JOB_DATA, register_and_login, login, logout


def _create_shortlisted_application(client):
    """Full flow up to SHORTLISTED status; returns (app_id, job_id)."""
    register_and_login(client, RECRUITER_DATA)
    resp = client.post("/api/jobs", json=JOB_DATA)
    job_id = resp.get_json()["data"]["_id"]
    logout(client)

    register_and_login(client, CANDIDATE_DATA)
    resp = client.post(f"/api/jobs/{job_id}/apply")
    app_id = resp.get_json()["data"]["_id"]
    logout(client)

    login(client, RECRUITER_DATA["email"], RECRUITER_DATA["password"])
    # Move to UNDER_REVIEW first, then SHORTLISTED
    client.put(f"/api/applications/{app_id}/status", json={"status": "UNDER_REVIEW"})
    client.put(f"/api/applications/{app_id}/status", json={"status": "SHORTLISTED"})
    return app_id, job_id


INTERVIEW_DATA = {
    "date": "2027-06-15",
    "time": "10:00",
    "type": "ONLINE",
    "meeting_link": "https://meet.google.com/test",
}


class TestInterviewScheduling:
    def test_schedule_interview_success(self, client):
        app_id, _ = _create_shortlisted_application(client)
        # Recruiter is still logged in
        resp = client.post("/api/interviews", json={"application_id": app_id, **INTERVIEW_DATA})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "SCHEDULED"
        assert data["data"]["type"] == "ONLINE"

    def test_schedule_interview_requires_recruiter(self, client):
        app_id, _ = _create_shortlisted_application(client)
        logout(client)
        login(client, CANDIDATE_DATA["email"], CANDIDATE_DATA["password"])
        resp = client.post("/api/interviews", json={"application_id": app_id, **INTERVIEW_DATA})
        assert resp.status_code == 403

    def test_schedule_interview_invalid_type(self, client):
        app_id, _ = _create_shortlisted_application(client)
        bad = {**INTERVIEW_DATA, "type": "TELEPATHIC"}
        resp = client.post("/api/interviews", json={"application_id": app_id, **bad})
        assert resp.status_code in (400, 422)

    def test_list_interviews_as_recruiter(self, client):
        app_id, _ = _create_shortlisted_application(client)
        client.post("/api/interviews", json={"application_id": app_id, **INTERVIEW_DATA})
        resp = client.get("/api/interviews")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["total"] >= 1

    def test_list_interviews_as_candidate(self, client):
        app_id, _ = _create_shortlisted_application(client)
        client.post("/api/interviews", json={"application_id": app_id, **INTERVIEW_DATA})
        logout(client)
        login(client, CANDIDATE_DATA["email"], CANDIDATE_DATA["password"])
        resp = client.get("/api/interviews")
        assert resp.status_code == 200

    def test_update_interview_status_to_cancelled(self, client):
        app_id, _ = _create_shortlisted_application(client)
        resp = client.post("/api/interviews", json={"application_id": app_id, **INTERVIEW_DATA})
        interview_id = resp.get_json()["data"]["_id"]
        resp2 = client.put(f"/api/interviews/{interview_id}", json={"status": "CANCELLED"})
        assert resp2.status_code == 200
        assert resp2.get_json()["data"]["status"] == "CANCELLED"

    def test_update_interview_other_recruiter_denied(self, client):
        app_id, _ = _create_shortlisted_application(client)
        resp = client.post("/api/interviews", json={"application_id": app_id, **INTERVIEW_DATA})
        interview_id = resp.get_json()["data"]["_id"]
        logout(client)
        other = {**RECRUITER_DATA, "email": "other2@co.com", "company_name": "OtherCo2"}
        register_and_login(client, other)
        resp2 = client.put(f"/api/interviews/{interview_id}", json={"status": "CANCELLED"})
        assert resp2.status_code == 403
