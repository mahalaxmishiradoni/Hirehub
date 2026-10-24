"""
Candidate model — inherits from User; demonstrates inheritance and method overriding.
"""
from datetime import datetime
from typing import Optional, List
from app.models.user import User


class Candidate(User):
    """
    Candidate profile model.
    Extends User with recruitment-specific profile data.
    """

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        password_hash: str,
        location: str = "",
        skills: Optional[List[str]] = None,
        education: Optional[List[dict]] = None,
        experience: Optional[List[dict]] = None,
        expected_salary: Optional[float] = None,
        notice_period: Optional[str] = None,
        resume_id=None,
        saved_jobs: Optional[List] = None,
        profile_id=None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id=None,
    ) -> None:
        super().__init__(
            name=name,
            email=email,
            phone=phone,
            password_hash=password_hash,
            role=User.ROLE_CANDIDATE,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
            _id=_id,
        )
        self.location = location
        self.skills = skills or []
        self.education = education or []
        self.experience = experience or []
        self.expected_salary = expected_salary
        self.notice_period = notice_period
        self.resume_id = resume_id
        self.saved_jobs = saved_jobs or []
        self.profile_id = profile_id  # Reference to candidates collection

    # --- Properties ---
    @property
    def total_experience(self) -> int:
        """Compute total years of experience from experience list."""
        total = 0
        for exp in self.experience:
            try:
                total += int(exp.get("years", 0))
            except (ValueError, TypeError):
                pass
        return total

    @property
    def skill_set(self) -> set:
        """Return skills as a set for fast lookup."""
        return {s.lower().strip() for s in self.skills}

    # --- Class method (overrides parent for role-specific construction) ---
    @classmethod
    def from_dict(cls, data: dict) -> "Candidate":
        return cls(
            _id=data.get("_id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            password_hash=data.get("password_hash", ""),
            location=data.get("location", ""),
            skills=data.get("skills", []),
            education=data.get("education", []),
            experience=data.get("experience", []),
            expected_salary=data.get("expected_salary"),
            notice_period=data.get("notice_period"),
            resume_id=data.get("resume_id"),
            saved_jobs=data.get("saved_jobs", []),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    # --- Instance method (overrides parent) ---
    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "location": self.location,
            "skills": self.skills,
            "education": self.education,
            "experience": self.experience,
            "expected_salary": self.expected_salary,
            "notice_period": self.notice_period,
            "resume_id": self.resume_id,
            "saved_jobs": self.saved_jobs,
        })
        return d

    def add_skill(self, skill: str) -> None:
        """Add a skill if not already present (case-insensitive)."""
        if skill.strip().lower() not in self.skill_set:
            self.skills.append(skill.strip())

    def remove_skill(self, skill: str) -> None:
        """Remove a skill by name (case-insensitive)."""
        self.skills = [s for s in self.skills if s.lower().strip() != skill.lower().strip()]

    def save_job(self, job_id) -> None:
        """Bookmark a job."""
        job_id_str = str(job_id)
        if job_id_str not in [str(j) for j in self.saved_jobs]:
            self.saved_jobs.append(job_id)

    def unsave_job(self, job_id) -> None:
        """Remove a bookmarked job."""
        job_id_str = str(job_id)
        self.saved_jobs = [j for j in self.saved_jobs if str(j) != job_id_str]

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} name={self.name}>"
