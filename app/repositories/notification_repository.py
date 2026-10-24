"""
Notification repository — CRUD against the `notifications` collection.
"""
from typing import Optional, Any
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class NotificationRepository(BaseRepository):
    collection_name = "notifications"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_by_user(self, user_id: Any, page: int = 1, per_page: int = 20) -> dict:
        oid = to_object_id(user_id)
        query = {"user_id": oid}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1)
        return self._paginate(cursor, page, per_page, total)

    def find_unread_by_user(self, user_id: Any) -> list:
        oid = to_object_id(user_id)
        return list(self.collection.find({"user_id": oid, "is_read": False}).sort("created_at", -1))

    def count_unread(self, user_id: Any) -> int:
        oid = to_object_id(user_id)
        return self.collection.count_documents({"user_id": oid, "is_read": False})

    def mark_read(self, notif_id: Any) -> bool:
        return self.update_by_id(notif_id, {"is_read": True})

    def mark_all_read(self, user_id: Any) -> int:
        oid = to_object_id(user_id)
        result = self.collection.update_many({"user_id": oid, "is_read": False}, {"$set": {"is_read": True}})
        return result.modified_count

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1)
        return self._paginate(cursor, page, per_page, total)
