"""
Tests for job creation, editing, search, and filtering.
"""
import pytest
from tests.conftest import CANDIDATE_DATA, RECRUITER_DATA, JOB_DATA, register_and_login, login, logout


def _register_recruiter(client):
    register_and_login(client, RECRUITER_DATA)


def _create_job_via_api(client) -> str:
    """Register recruiter, log in, create a job, return job _id."""
    register_and_login(client, RECRUITER_DATA)
    resp = client.post("/api/jobs", json=JOB_DATA)
    assert resp.status_code == 201
    return resp.get_json()["data"]["_id"]


class TestJobCreation:
    def test_create_job_requires_recruiter(self, client):
        register_and_login(client, CANDIDATE_DATA)
        resp = client.post("/api/jobs", json=JOB_DATA)
        assert resp.status_code == 403

    def test_create_job_success(self, client, app):
        _register_recruiter(client)
        resp = client.post("/api/jobs", json=JOB_DATA)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["title"] == JOB_DATA["title"]

    def test_create_job_missing_title(self, client):
        _register_recruiter(client)
        bad = {**JOB_DATA, "title": ""}
        resp = client.post("/api/jobs", json=bad)
        assert resp.status_code == 422
        assert resp.get_json()["error_code"] == "VALIDATION_ERROR"

    def test_create_job_invalid_work_mode(self, client):
        _register_recruiter(client)
        bad = {**JOB_DATA, "work_mode": "SPACESHIP"}
        resp = client.post("/api/jobs", json=bad)
        assert resp.status_code == 422

    def test_create_job_missing_location(self, client):
        _register_recruiter(client)
        bad = {**JOB_DATA, "location": ""}
        resp = client.post("/api/jobs", json=bad)
        assert resp.status_code == 422


class TestJobRetrieval:
    def test_get_job_by_id(self, client):
        job_id = _create_job_via_api(client)
        logout(client)
        resp = client.get(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["title"] == JOB_DATA["title"]

    def test_get_nonexistent_job(self, client):
        resp = client.get("/api/jobs/000000000000000000000000")
        assert resp.status_code == 404
        assert resp.get_json()["error_code"] == "JOB_NOT_FOUND"

    def test_list_jobs_returns_items(self, client):
        _create_job_via_api(client)
        logout(client)
        resp = client.get("/api/jobs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"]["total"] >= 1


class TestJobSearch:
    def test_search_by_keyword(self, client):
        _create_job_via_api(client)
        logout(client)
        resp = client.get("/api/jobs?keyword=Python")
        assert resp.status_code == 200
        items = resp.get_json()["data"]["items"]
        assert any("python" in j["title"].lower() for j in items)

    def test_search_by_location(self, client):
        _create_job_via_api(client)
        logout(client)
        resp = client.get("/api/jobs?location=Bangalore")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["total"] >= 1

    def test_search_by_work_mode(self, client):
        _create_job_via_api(client)
        logout(client)
        resp = client.get("/api/jobs?work_mode=HYBRID")
        assert resp.status_code == 200
        items = resp.get_json()["data"]["items"]
        assert all(j.get("work_mode") == "HYBRID" for j in items)

    def test_search_no_results(self, client):
        _create_job_via_api(client)
        logout(client)
        resp = client.get("/api/jobs?keyword=NONEXISTENTJOB12345")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["total"] == 0

    def test_pagination_defaults(self, client):
        _create_job_via_api(client)
        logout(client)
        resp = client.get("/api/jobs?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "items" in data
        assert "total_pages" in data


class TestJobUpdate:
    def test_update_own_job(self, client):
        job_id = _create_job_via_api(client)
        resp = client.put(f"/api/jobs/{job_id}", json={**JOB_DATA, "title": "Senior Python Dev"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["title"] == "Senior Python Dev"

    def test_update_job_by_other_recruiter_denied(self, client):
        job_id = _create_job_via_api(client)
        logout(client)
        # Register a second recruiter
        other = {**RECRUITER_DATA, "email": "other@co.com", "company_name": "OtherCo"}
        register_and_login(client, other)
        resp = client.put(f"/api/jobs/{job_id}", json={**JOB_DATA, "title": "Stolen"})
        assert resp.status_code == 403

    def test_delete_own_job(self, client):
        job_id = _create_job_via_api(client)
        resp = client.delete(f"/api/jobs/{job_id}")
        assert resp.status_code == 200
        # Verify gone
        resp2 = client.get(f"/api/jobs/{job_id}")
        assert resp2.status_code == 404
