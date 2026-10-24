"""
Application repository — CRUD against the `applications` collection.
"""
from typing import Optional, Any, List
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class ApplicationRepository(BaseRepository):
    collection_name = "applications"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("applied_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_candidate(self, candidate_id: Any, page: int = 1, per_page: int = 20) -> dict:
        oid = to_object_id(candidate_id)
        query = {"candidate_id": oid}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("applied_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_job(self, job_id: Any, page: int = 1, per_page: int = 20) -> dict:
        oid = to_object_id(job_id)
        query = {"job_id": oid}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("applied_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_candidate_and_job(self, candidate_id: Any, job_id: Any) -> Optional[dict]:
        cid = to_object_id(candidate_id)
        jid = to_object_id(job_id)
        return self.collection.find_one({"candidate_id": cid, "job_id": jid})

    def find_by_recruiter_jobs(self, job_ids: List[Any], page: int = 1, per_page: int = 20) -> dict:
        oids = [to_object_id(j) for j in job_ids if to_object_id(j)]
        query = {"job_id": {"$in": oids}}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("applied_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def update_status(self, application_id: Any, status: str, notes: str = "") -> bool:
        update = {"status": status}
        if notes:
            update["recruiter_notes"] = notes
        return self.update_by_id(application_id, update)

    def set_interview(self, application_id: Any, interview_id: Any) -> bool:
        return self.update_by_id(application_id, {"interview_id": to_object_id(interview_id)})

    def count_by_status(self, candidate_id: Any) -> dict:
        """Aggregate application counts grouped by status for a candidate."""
        oid = to_object_id(candidate_id)
        pipeline = [
            {"$match": {"candidate_id": oid}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        result = list(self.collection.aggregate(pipeline))
        return {r["_id"]: r["count"] for r in result}
