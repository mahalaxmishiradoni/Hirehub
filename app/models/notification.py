"""
Notification domain model.
"""
from datetime import datetime
from typing import Optional


class Notification:
    """
    In-app notification for users.
    """

    TYPES: set = {
        "REGISTRATION",
        "APPLICATION_SUBMITTED",
        "APPLICATION_SHORTLISTED",
        "APPLICATION_REJECTED",
        "INTERVIEW_SCHEDULED",
        "INTERVIEW_CANCELLED",
        "CANDIDATE_SELECTED",
        "GENERAL",
    }

    def __init__(
        self,
        user_id,
        title: str,
        message: str,
        notif_type: str = "GENERAL",
        resource_id=None,
        is_read: bool = False,
        created_at: Optional[datetime] = None,
        _id=None,
    ) -> None:
        self._id = _id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notif_type = notif_type
        self.resource_id = resource_id
        self.is_read = is_read
        self.created_at = created_at or datetime.utcnow()

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        return cls(
            _id=data.get("_id"),
            user_id=data.get("user_id"),
            title=data.get("title", ""),
            message=data.get("message", ""),
            notif_type=data.get("type", "GENERAL"),
            resource_id=data.get("resource_id"),
            is_read=data.get("is_read", False),
            created_at=data.get("created_at"),
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "type": self.notif_type,
            "resource_id": self.resource_id,
            "is_read": self.is_read,
            "created_at": self.created_at,
        }

    def mark_read(self) -> None:
        self.is_read = True

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.notif_type} read={self.is_read}>"
