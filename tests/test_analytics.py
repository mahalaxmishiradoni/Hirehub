"""
Tests for analytics repository and service aggregations.
"""
import pytest
from bson import ObjectId
from datetime import datetime


def _seed_basic_data(db):
    """Insert minimal fixture data for analytics tests."""
    # Users
    u_cand = db.users.insert_one({"name": "C1", "email": "c1@x.com", "role": "CANDIDATE", "is_active": True, "created_at": datetime.utcnow()}).inserted_id
    u_rec  = db.users.insert_one({"name": "R1", "email": "r1@x.com", "role": "RECRUITER", "is_active": True, "created_at": datetime.utcnow()}).inserted_id

    # Company
    co = db.companies.insert_one({"name": "TestCo", "recruiter_id": u_rec, "is_verified": True}).inserted_id

    # Jobs
    j1 = db.jobs.insert_one({
        "title": "Dev", "skills": ["python", "sql"], "location": "Bangalore",
        "work_mode": "REMOTE", "employment_type": "FULL_TIME",
        "recruiter_id": u_rec, "company_id": co,
        "status": "OPEN", "salary_min": 10, "salary_max": 20,
        "experience_min": 1, "experience_max": 5,
        "posted_date": datetime.utcnow(), "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
    }).inserted_id
    j2 = db.jobs.insert_one({
        "title": "Analyst", "skills": ["python", "excel"], "location": "Mumbai",
        "work_mode": "ONSITE", "employment_type": "FULL_TIME",
        "recruiter_id": u_rec, "company_id": co,
        "status": "OPEN", "salary_min": 8, "salary_max": 15,
        "experience_min": 0, "experience_max": 3,
        "posted_date": datetime.utcnow(), "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
    }).inserted_id

    # Candidate profile
    cand = db.candidates.insert_one({"user_id": u_cand, "name": "C1", "email": "c1@x.com", "skills": ["python"]}).inserted_id

    # Applications
    a1 = db.applications.insert_one({
        "candidate_id": cand, "job_id": j1,
        "status": "SHORTLISTED", "applied_at": datetime.utcnow(), "updated_at": datetime.utcnow()
    }).inserted_id
    a2 = db.applications.insert_one({
        "candidate_id": cand, "job_id": j2,
        "status": "APPLIED", "applied_at": datetime.utcnow(), "updated_at": datetime.utcnow()
    }).inserted_id

    return {"u_rec": u_rec, "cand": cand, "j1": j1, "j2": j2, "a1": a1, "co": co}


class TestAnalyticsRepository:
    def test_admin_overview(self, app, db):
        with app.app_context():
            _seed_basic_data(db)
            from app.repositories.analytics_repository import AnalyticsRepository
            repo = AnalyticsRepository()
            overview = repo.admin_overview()
            assert overview["total_users"] >= 2
            assert overview["candidates"] >= 1
            assert overview["recruiters"] >= 1
            assert overview["total_jobs"] >= 2
            assert overview["total_applications"] >= 2

    def test_jobs_by_skill(self, app, db):
        with app.app_context():
            _seed_basic_data(db)
            from app.repositories.analytics_repository import AnalyticsRepository
            repo = AnalyticsRepository()
            result = repo.jobs_by_skill(limit=10)
            skill_names = [r["_id"] for r in result]
            assert "python" in skill_names
            # python appears in 2 jobs
            python_count = next(r["count"] for r in result if r["_id"] == "python")
            assert python_count >= 2

    def test_applications_by_status(self, app, db):
        with app.app_context():
            _seed_basic_data(db)
            from app.repositories.analytics_repository import AnalyticsRepository
            repo = AnalyticsRepository()
            result = repo.applications_by_status()
            statuses = {r["_id"] for r in result}
            assert "SHORTLISTED" in statuses or "APPLIED" in statuses

    def test_recruiter_stats(self, app, db):
        with app.app_context():
            ids = _seed_basic_data(db)
            from app.repositories.analytics_repository import AnalyticsRepository
            repo = AnalyticsRepository()
            stats = repo.recruiter_stats(ids["u_rec"])
            assert stats["total_jobs"] >= 2
            assert stats["total_applications"] >= 2

    def test_candidate_stats(self, app, db):
        with app.app_context():
            ids = _seed_basic_data(db)
            from app.repositories.analytics_repository import AnalyticsRepository
            repo = AnalyticsRepository()
            stats = repo.candidate_stats(ids["cand"])
            assert stats["total_applications"] >= 2

    def test_monthly_applications_returns_12_months(self, app, db):
        with app.app_context():
            _seed_basic_data(db)
            from app.services.analytics_service import AnalyticsService
            svc = AnalyticsService()
            result = svc.get_monthly_applications()
            assert len(result["labels"]) == 12
            assert len(result["data"]) == 12

    def test_monthly_registrations_returns_12_months(self, app, db):
        with app.app_context():
            _seed_basic_data(db)
            from app.services.analytics_service import AnalyticsService
            svc = AnalyticsService()
            result = svc.get_monthly_registrations()
            assert len(result["labels"]) == 12

    def test_jobs_by_location(self, app, db):
        with app.app_context():
            _seed_basic_data(db)
            from app.repositories.analytics_repository import AnalyticsRepository
            repo = AnalyticsRepository()
            result = repo.jobs_by_location()
            locations = [r["_id"] for r in result]
            assert "Bangalore" in locations or "Mumbai" in locations
