"""
Application domain model.
"""
from datetime import datetime
from typing import Optional


class Application:
    """
    Represents a candidate's application to a job.
    """

    # Valid statuses and allowed transitions
    STATUSES: set = {
        "APPLIED", "UNDER_REVIEW", "SHORTLISTED",
        "INTERVIEW_SCHEDULED", "SELECTED", "REJECTED", "WITHDRAWN",
    }

    # Allowed status transitions: current → set of allowed next statuses
    TRANSITIONS: dict = {
        "APPLIED": {"UNDER_REVIEW", "SHORTLISTED", "REJECTED", "WITHDRAWN"},
        "UNDER_REVIEW": {"SHORTLISTED", "REJECTED"},
        "SHORTLISTED": {"INTERVIEW_SCHEDULED", "REJECTED"},
        "INTERVIEW_SCHEDULED": {"SELECTED", "REJECTED"},
        "SELECTED": set(),
        "REJECTED": set(),
        "WITHDRAWN": set(),
    }

    def __init__(
        self,
        candidate_id,
        job_id,
        status: str = "APPLIED",
        applied_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        recruiter_notes: str = "",
        interview_id=None,
        _id=None,
    ) -> None:
        self._id = _id
        self.candidate_id = candidate_id
        self.job_id = job_id
        self.status = status
        self.applied_at = applied_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.recruiter_notes = recruiter_notes
        self.interview_id = interview_id

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    @classmethod
    def from_dict(cls, data: dict) -> "Application":
        return cls(
            _id=data.get("_id"),
            candidate_id=data.get("candidate_id"),
            job_id=data.get("job_id"),
            status=data.get("status", "APPLIED"),
            applied_at=data.get("applied_at"),
            updated_at=data.get("updated_at"),
            recruiter_notes=data.get("recruiter_notes", ""),
            interview_id=data.get("interview_id"),
        )

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "status": self.status,
            "applied_at": self.applied_at,
            "updated_at": self.updated_at,
            "recruiter_notes": self.recruiter_notes,
            "interview_id": self.interview_id,
        }

    def can_transition_to(self, new_status: str) -> bool:
        """Check whether the status transition is valid."""
        return new_status in self.TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status: str) -> None:
        """Apply a status transition."""
        from app.exceptions.app_exceptions import InvalidApplicationStatusError
        if not self.can_transition_to(new_status):
            raise InvalidApplicationStatusError(
                f"Cannot transition application from {self.status} to {new_status}."
            )
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def withdraw(self) -> None:
        """Candidate withdraws the application."""
        if self.status in {"SELECTED", "REJECTED", "WITHDRAWN"}:
            from app.exceptions.app_exceptions import InvalidApplicationStatusError
            raise InvalidApplicationStatusError("Cannot withdraw application in current status.")
        self.status = "WITHDRAWN"
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Application id={self.id} status={self.status}>"
