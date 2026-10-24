"""
Abstract base repository — defines the CRUD interface all repositories implement.
Demonstrates: abstraction, inheritance, polymorphism.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List
from bson import ObjectId
from datetime import datetime
from app.extensions import get_db
from app.utils.helpers import to_object_id


class BaseRepository(ABC):
    """
    Abstract base for all repositories.
    Subclasses must declare `collection_name` and may override any method.
    """

    collection_name: str = ""

    def __init__(self) -> None:
        if not self.collection_name:
            raise NotImplementedError("Subclasses must define collection_name.")

    @property
    def collection(self):
        """Return the MongoDB collection."""
        return get_db()[self.collection_name]

    # ------------------------------------------------------------------ #
    # Abstract interface
    # ------------------------------------------------------------------ #
    @abstractmethod
    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        """Return a single document by _id."""

    @abstractmethod
    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 20) -> dict:
        """Return paginated documents matching optional filters."""

    # ------------------------------------------------------------------ #
    # Concrete shared helpers
    # ------------------------------------------------------------------ #
    def insert(self, document: dict) -> Any:
        """Insert a document and return the inserted _id."""
        result = self.collection.insert_one(document)
        return result.inserted_id

    def update_by_id(self, doc_id: Any, update_data: dict) -> bool:
        """Update a document by _id; returns True if matched."""
        oid = to_object_id(doc_id)
        if not oid:
            return False
        update_data["updated_at"] = datetime.utcnow()
        result = self.collection.update_one({"_id": oid}, {"$set": update_data})
        return result.matched_count > 0

    def delete_by_id(self, doc_id: Any) -> bool:
        """Delete a document by _id; returns True if deleted."""
        oid = to_object_id(doc_id)
        if not oid:
            return False
        result = self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0

    def count(self, filters: dict = None) -> int:
        """Count documents matching optional filters."""
        return self.collection.count_documents(filters or {})

    def _paginate(self, cursor, page: int, per_page: int, total: int) -> dict:
        """Build a pagination response dict."""
        items = list(cursor.skip((page - 1) * per_page).limit(per_page))
        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": max(1, (total + per_page - 1) // per_page),
            "has_prev": page > 1,
            "has_next": page < max(1, (total + per_page - 1) // per_page),
        }
