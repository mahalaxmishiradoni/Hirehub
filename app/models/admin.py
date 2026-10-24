"""
Admin model — inherits from User.
"""
from datetime import datetime
from typing import Optional
from app.models.user import User


class Admin(User):
    """
    Admin user model.
    Admin accounts are created directly (not via public registration).
    """

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        password_hash: str,
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
            role=User.ROLE_ADMIN,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
            _id=_id,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Admin":
        return cls(
            _id=data.get("_id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            password_hash=data.get("password_hash", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    # --- Static method: factory for seeding admin accounts ---
    @staticmethod
    def create_default(name: str, email: str, password: str) -> "Admin":
        """Create a default admin (for seeding/scripts only)."""
        return Admin(
            name=name,
            email=email,
            phone="0000000000",
            password_hash=User.hash_password(password),
        )

    def __repr__(self) -> str:
        return f"<Admin id={self.id} email={self.email}>"
