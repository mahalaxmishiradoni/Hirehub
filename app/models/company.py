"""
Company domain model — composition with Recruiter.
"""
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Company:
    """
    Represents a company in HireHub.
    Associated with one or more recruiters.
    """

    def __init__(
        self,
        name: str,
        recruiter_id,
        description: str = "",
        website: str = "",
        location: str = "",
        industry: str = "",
        size: str = "",
        logo_url: str = "",
        is_verified: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id=None,
    ) -> None:
        self._id = _id
        self.name = name
        self.recruiter_id = recruiter_id
        self.description = description
        self.website = website
        self.location = location
        self.industry = industry
        self.size = size
        self.logo_url = logo_url
        self.is_verified = is_verified
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    @classmethod
    def from_dict(cls, data: dict) -> "Company":
        return cls(
            _id=data.get("_id"),
            name=data.get("name", ""),
            recruiter_id=data.get("recruiter_id"),
            description=data.get("description", ""),
            website=data.get("website", ""),
            location=data.get("location", ""),
            industry=data.get("industry", ""),
            size=data.get("size", ""),
            logo_url=data.get("logo_url", ""),
            is_verified=data.get("is_verified", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "recruiter_id": self.recruiter_id,
            "description": self.description,
            "website": self.website,
            "location": self.location,
            "industry": self.industry,
            "size": self.size,
            "logo_url": self.logo_url,
            "is_verified": self.is_verified,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def verify(self) -> None:
        """Mark this company as verified by admin."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name}>"
