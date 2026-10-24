"""
Resume repository — CRUD against the `resumes` collection.
"""
from typing import Optional, Any
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class ResumeRepository(BaseRepository):
    collection_name = "resumes"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_by_candidate(self, candidate_id: Any) -> Optional[dict]:
        oid = to_object_id(candidate_id)
        return self.collection.find_one({"candidate_id": oid}) if oid else None

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("uploaded_at", -1)
        return self._paginate(cursor, page, per_page, total)
