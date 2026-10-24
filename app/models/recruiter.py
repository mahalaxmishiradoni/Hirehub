"""
Recruiter model — inherits from User.
"""
from datetime import datetime
from typing import Optional
from app.models.user import User


class Recruiter(User):
    """
    Recruiter profile model.
    Associated with one Company.
    """

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        password_hash: str,
        company_id=None,
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
            role=User.ROLE_RECRUITER,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
            _id=_id,
        )
        self.company_id = company_id
        self.profile_id = profile_id

    @classmethod
    def from_dict(cls, data: dict) -> "Recruiter":
        return cls(
            _id=data.get("_id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            password_hash=data.get("password_hash", ""),
            company_id=data.get("company_id"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["company_id"] = self.company_id
        return d

    def __repr__(self) -> str:
        return f"<Recruiter id={self.id} name={self.name}>"
