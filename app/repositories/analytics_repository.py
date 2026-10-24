"""
Analytics repository — MongoDB aggregation pipelines.
"""
from typing import List
from app.extensions import get_db


class AnalyticsRepository:
    """Runs aggregation pipelines; no BaseRepository needed (no standard CRUD)."""

    @property
    def db(self):
        return get_db()

    # ------------------------------------------------------------------ #
    # Jobs analytics
    # ------------------------------------------------------------------ #
    def jobs_by_skill(self, limit: int = 15) -> List[dict]:
        pipeline = [
            {"$match": {"status": "OPEN"}},
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        return list(self.db.jobs.aggregate(pipeline))

    def jobs_by_location(self, limit: int = 10) -> List[dict]:
        pipeline = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        return list(self.db.jobs.aggregate(pipeline))

    def jobs_by_work_mode(self) -> List[dict]:
        pipeline = [
            {"$group": {"_id": "$work_mode", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        return list(self.db.jobs.aggregate(pipeline))

    def jobs_by_employment_type(self) -> List[dict]:
        pipeline = [
            {"$group": {"_id": "$employment_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        return list(self.db.jobs.aggregate(pipeline))

    # ------------------------------------------------------------------ #
    # Applications analytics
    # ------------------------------------------------------------------ #
    def applications_by_status(self) -> List[dict]:
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        return list(self.db.applications.aggregate(pipeline))

    def applications_by_job(self, limit: int = 10) -> List[dict]:
        pipeline = [
            {"$group": {"_id": "$job_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "job",
                }
            },
            {"$unwind": {"path": "$job", "preserveNullAndEmptyArrays": True}},
            {"$project": {"job_title": "$job.title", "count": 1}},
        ]
        return list(self.db.applications.aggregate(pipeline))

    def monthly_applications(self, year: int = None) -> List[dict]:
        import datetime
        y = year or datetime.datetime.utcnow().year
        pipeline = [
            {
                "$match": {
                    "applied_at": {
                        "$gte": datetime.datetime(y, 1, 1),
                        "$lt": datetime.datetime(y + 1, 1, 1),
                    }
                }
            },
            {
                "$group": {
                    "_id": {"$month": "$applied_at"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        return list(self.db.applications.aggregate(pipeline))

    # ------------------------------------------------------------------ #
    # User / registration analytics
    # ------------------------------------------------------------------ #
    def monthly_registrations(self, year: int = None) -> List[dict]:
        import datetime
        y = year or datetime.datetime.utcnow().year
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": datetime.datetime(y, 1, 1),
                        "$lt": datetime.datetime(y + 1, 1, 1),
                    }
                }
            },
            {
                "$group": {
                    "_id": {"month": {"$month": "$created_at"}, "role": "$role"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.month": 1}},
        ]
        return list(self.db.users.aggregate(pipeline))

    def user_counts_by_role(self) -> dict:
        pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
        ]
        result = list(self.db.users.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in result}

    # ------------------------------------------------------------------ #
    # Recruiter-specific
    # ------------------------------------------------------------------ #
    def recruiter_stats(self, recruiter_id) -> dict:
        from app.utils.helpers import to_object_id
        oid = to_object_id(recruiter_id)
        total_jobs = self.db.jobs.count_documents({"recruiter_id": oid})
        active_jobs = self.db.jobs.count_documents({"recruiter_id": oid, "status": "OPEN"})
        job_ids = [j["_id"] for j in self.db.jobs.find({"recruiter_id": oid}, {"_id": 1})]
        total_apps = self.db.applications.count_documents({"job_id": {"$in": job_ids}})
        shortlisted = self.db.applications.count_documents({"job_id": {"$in": job_ids}, "status": "SHORTLISTED"})
        selected = self.db.applications.count_documents({"job_id": {"$in": job_ids}, "status": "SELECTED"})
        interviews = self.db.interviews.count_documents({"recruiter_id": oid})
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_apps,
            "shortlisted": shortlisted,
            "selected": selected,
            "interviews": interviews,
        }

    # ------------------------------------------------------------------ #
    # Candidate-specific
    # ------------------------------------------------------------------ #
    def candidate_stats(self, candidate_id) -> dict:
        from app.utils.helpers import to_object_id
        oid = to_object_id(candidate_id)
        total = self.db.applications.count_documents({"candidate_id": oid})
        pipeline = [
            {"$match": {"candidate_id": oid}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        by_status = {r["_id"]: r["count"] for r in self.db.applications.aggregate(pipeline)}
        interviews = self.db.interviews.count_documents({"candidate_id": oid})
        return {
            "total_applications": total,
            "by_status": by_status,
            "shortlisted": by_status.get("SHORTLISTED", 0),
            "selected": by_status.get("SELECTED", 0),
            "interviews": interviews,
        }

    # ------------------------------------------------------------------ #
    # Admin overview
    # ------------------------------------------------------------------ #
    def admin_overview(self) -> dict:
        roles = self.user_counts_by_role()
        return {
            "total_users": sum(roles.values()),
            "candidates": roles.get("CANDIDATE", 0),
            "recruiters": roles.get("RECRUITER", 0),
            "admins": roles.get("ADMIN", 0),
            "total_companies": self.db.companies.count_documents({}),
            "total_jobs": self.db.jobs.count_documents({}),
            "open_jobs": self.db.jobs.count_documents({"status": "OPEN"}),
            "total_applications": self.db.applications.count_documents({}),
            "total_interviews": self.db.interviews.count_documents({}),
            "selected_candidates": self.db.applications.count_documents({"status": "SELECTED"}),
        }

    def top_skills(self, limit: int = 10) -> List[dict]:
        return self.jobs_by_skill(limit)

    def applications_by_company(self, limit: int = 10) -> List[dict]:
        pipeline = [
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job",
                }
            },
            {"$unwind": "$job"},
            {
                "$lookup": {
                    "from": "companies",
                    "localField": "job.company_id",
                    "foreignField": "_id",
                    "as": "company",
                }
            },
            {"$unwind": "$company"},
            {"$group": {"_id": "$company.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        return list(self.db.applications.aggregate(pipeline))
