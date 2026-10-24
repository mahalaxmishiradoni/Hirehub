"""
User repository — CRUD against the `users` collection.
"""
from typing import Optional, Any
from bson import ObjectId
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class UserRepository(BaseRepository):
    collection_name = "users"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        if not oid:
            return None
        return self.collection.find_one({"_id": oid})

    def find_by_email(self, email: str) -> Optional[dict]:
        return self.collection.find_one({"email": email.lower().strip()})

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_role(self, role: str, page: int = 1, per_page: int = 20) -> dict:
        return self.find_all({"role": role}, page, per_page)

    def email_exists(self, email: str) -> bool:
        return self.collection.count_documents({"email": email.lower().strip()}) > 0

    def set_active(self, user_id: Any, is_active: bool) -> bool:
        return self.update_by_id(user_id, {"is_active": is_active})
