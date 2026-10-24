"""
Job domain model.
"""
from datetime import datetime
from typing import Optional, List


class Job:
    """
    Represents a job posting.
    """

    # Class-level constants (polymorphism through enums)
    WORK_MODES: set = {"REMOTE", "HYBRID", "ONSITE"}
    EMPLOYMENT_TYPES: set = {"FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT"}
    STATUSES: set = {"OPEN", "CLOSED", "EXPIRED"}

    # Class variable: default status
    DEFAULT_STATUS: str = "OPEN"

    def __init__(
        self,
        company_id,
        recruiter_id,
        title: str,
        description: str,
        location: str,
        work_mode: str = "ONSITE",
        employment_type: str = "FULL_TIME",
        skills: Optional[List[str]] = None,
        experience_min: int = 0,
        experience_max: int = 0,
        salary_min: float = 0.0,
        salary_max: float = 0.0,
        deadline=None,
        status: str = "OPEN",
        posted_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id=None,
    ) -> None:
        self._id = _id
        self.company_id = company_id
        self.recruiter_id = recruiter_id
        self.title = title
        self.description = description
        self.location = location
        self.work_mode = work_mode
        self.employment_type = employment_type
        self.skills = skills or []
        self.experience_min = experience_min
        self.experience_max = experience_max
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.deadline = deadline
        self.status = status
        self.posted_date = posted_date or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    @property
    def is_open(self) -> bool:
        return self.status == "OPEN"

    @property
    def skill_set(self) -> set:
        return {s.lower().strip() for s in self.skills}

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        return cls(
            _id=data.get("_id"),
            company_id=data.get("company_id"),
            recruiter_id=data.get("recruiter_id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            location=data.get("location", ""),
            work_mode=data.get("work_mode", "ONSITE"),
            employment_type=data.get("employment_type", "FULL_TIME"),
            skills=data.get("skills", []),
            experience_min=data.get("experience_min", 0),
            experience_max=data.get("experience_max", 0),
            salary_min=data.get("salary_min", 0.0),
            salary_max=data.get("salary_max", 0.0),
            deadline=data.get("deadline"),
            status=data.get("status", "OPEN"),
            posted_date=data.get("posted_date"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "company_id": self.company_id,
            "recruiter_id": self.recruiter_id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "work_mode": self.work_mode,
            "employment_type": self.employment_type,
            "skills": self.skills,
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "deadline": self.deadline,
            "status": self.status,
            "posted_date": self.posted_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def close(self) -> None:
        """Close this job."""
        self.status = "CLOSED"
        self.updated_at = datetime.utcnow()

    def expire(self) -> None:
        """Mark as expired."""
        self.status = "EXPIRED"
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} status={self.status}>"
