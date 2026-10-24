"""
Recruiter repository — CRUD against the `recruiters` collection.
"""
from typing import Optional, Any
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class RecruiterRepository(BaseRepository):
    collection_name = "recruiters"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_by_user_id(self, user_id: Any) -> Optional[dict]:
        oid = to_object_id(user_id)
        return self.collection.find_one({"user_id": oid}) if oid else None

    def find_by_company_id(self, company_id: Any) -> Optional[dict]:
        oid = to_object_id(company_id)
        return self.collection.find_one({"company_id": oid}) if oid else None

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1)
        return self._paginate(cursor, page, per_page, total)
