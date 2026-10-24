"""
Interview repository — CRUD against the `interviews` collection.
"""
from typing import Optional, Any, List
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class InterviewRepository(BaseRepository):
    collection_name = "interviews"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("date", 1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_candidate(self, candidate_id: Any, page: int = 1, per_page: int = 20) -> dict:
        oid = to_object_id(candidate_id)
        query = {"candidate_id": oid}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("date", 1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_recruiter(self, recruiter_id: Any, page: int = 1, per_page: int = 20) -> dict:
        oid = to_object_id(recruiter_id)
        query = {"recruiter_id": oid}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("date", 1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_application(self, application_id: Any) -> Optional[dict]:
        oid = to_object_id(application_id)
        return self.collection.find_one({"application_id": oid})

    def update_status(self, interview_id: Any, status: str, feedback: str = "") -> bool:
        update = {"status": status}
        if feedback:
            update["feedback"] = feedback
        return self.update_by_id(interview_id, update)
