"""
Interview domain model.
"""
from datetime import datetime
from typing import Optional


class Interview:
    """
    Represents a scheduled interview linked to an application.
    """

    TYPES: set = {"ONLINE", "PHONE", "IN_PERSON"}
    STATUSES: set = {"SCHEDULED", "COMPLETED", "CANCELLED"}

    def __init__(
        self,
        application_id,
        candidate_id,
        recruiter_id,
        date,
        time: str,
        interview_type: str = "ONLINE",
        meeting_link: str = "",
        status: str = "SCHEDULED",
        feedback: str = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id=None,
    ) -> None:
        self._id = _id
        self.application_id = application_id
        self.candidate_id = candidate_id
        self.recruiter_id = recruiter_id
        self.date = date
        self.time = time
        self.interview_type = interview_type
        self.meeting_link = meeting_link
        self.status = status
        self.feedback = feedback
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    @classmethod
    def from_dict(cls, data: dict) -> "Interview":
        return cls(
            _id=data.get("_id"),
            application_id=data.get("application_id"),
            candidate_id=data.get("candidate_id"),
            recruiter_id=data.get("recruiter_id"),
            date=data.get("date"),
            time=data.get("time", ""),
            interview_type=data.get("type", "ONLINE"),
            meeting_link=data.get("meeting_link", ""),
            status=data.get("status", "SCHEDULED"),
            feedback=data.get("feedback", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "application_id": self.application_id,
            "candidate_id": self.candidate_id,
            "recruiter_id": self.recruiter_id,
            "date": self.date,
            "time": self.time,
            "type": self.interview_type,
            "meeting_link": self.meeting_link,
            "status": self.status,
            "feedback": self.feedback,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def cancel(self) -> None:
        self.status = "CANCELLED"
        self.updated_at = datetime.utcnow()

    def complete(self, feedback: str = "") -> None:
        self.status = "COMPLETED"
        self.feedback = feedback
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Interview id={self.id} date={self.date} status={self.status}>"
