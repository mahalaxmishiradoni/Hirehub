"""
Company repository — CRUD against the `companies` collection.
"""
from typing import Optional, Any
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class CompanyRepository(BaseRepository):
    collection_name = "companies"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_by_name(self, name: str) -> Optional[dict]:
        return self.collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    def find_by_recruiter_id(self, recruiter_id: Any) -> Optional[dict]:
        oid = to_object_id(recruiter_id)
        return self.collection.find_one({"recruiter_id": oid}) if oid else None

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("name", 1)
        return self._paginate(cursor, page, per_page, total)

    def set_verified(self, company_id: Any, verified: bool) -> bool:
        return self.update_by_id(company_id, {"is_verified": verified})
