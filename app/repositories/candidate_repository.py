"""
Candidate repository — CRUD against the `candidates` collection.
"""
from typing import Optional, Any, List
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class CandidateRepository(BaseRepository):
    collection_name = "candidates"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_by_user_id(self, user_id: Any) -> Optional[dict]:
        oid = to_object_id(user_id)
        return self.collection.find_one({"user_id": oid}) if oid else None

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def search_by_skills(self, skills: List[str], page: int = 1, per_page: int = 20) -> dict:
        """Find candidates who have any of the given skills (case-insensitive)."""
        lower_skills = [s.lower() for s in skills]
        query = {"skills": {"$elemMatch": {"$in": lower_skills}}}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def update_resume(self, candidate_id: Any, resume_id: Any) -> bool:
        return self.update_by_id(candidate_id, {"resume_id": to_object_id(resume_id)})

    def add_saved_job(self, candidate_id: Any, job_id: Any) -> bool:
        oid = to_object_id(candidate_id)
        jid = to_object_id(job_id)
        if not oid or not jid:
            return False
        result = self.collection.update_one(
            {"_id": oid},
            {"$addToSet": {"saved_jobs": jid}},
        )
        return result.modified_count > 0

    def remove_saved_job(self, candidate_id: Any, job_id: Any) -> bool:
        oid = to_object_id(candidate_id)
        jid = to_object_id(job_id)
        if not oid or not jid:
            return False
        result = self.collection.update_one(
            {"_id": oid},
            {"$pull": {"saved_jobs": jid}},
        )
        return result.modified_count > 0
