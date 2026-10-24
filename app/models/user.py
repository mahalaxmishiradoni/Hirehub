"""
User domain model — base class for all roles.
Demonstrates: classes, constructors, instance variables, class variables,
class methods, static methods, properties, encapsulation, abstraction.
"""
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional


class User:
    """
    Base user model.  Sub-classed by Candidate, Recruiter, and Admin.
    """

    # Class-level role constants
    ROLE_CANDIDATE: str = "CANDIDATE"
    ROLE_RECRUITER: str = "RECRUITER"
    ROLE_ADMIN: str = "ADMIN"
    VALID_ROLES: set = {ROLE_CANDIDATE, ROLE_RECRUITER, ROLE_ADMIN}

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        password_hash: str,
        role: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id=None,
    ) -> None:
        self._id = _id
        self.name = name
        self._email = email.lower().strip()
        self.phone = phone
        self._password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # --- Properties (encapsulation) ---
    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value.lower().strip()

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    # --- Static methods ---
    @staticmethod
    def hash_password(plain: str) -> str:
        """Return a bcrypt hash of the plain-text password."""
        return generate_password_hash(plain)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify a plain-text password against its hash."""
        return check_password_hash(hashed, plain)

    # --- Class methods ---
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Construct a User from a MongoDB document."""
        return cls(
            _id=data.get("_id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            password_hash=data.get("password_hash", ""),
            role=data.get("role", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    # --- Instance methods ---
    def to_dict(self) -> dict:
        """Serialise to a dict suitable for MongoDB storage."""
        return {
            "name": self.name,
            "email": self._email,
            "phone": self.phone,
            "password_hash": self._password_hash,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_safe_dict(self) -> dict:
        """Serialise without the password hash (safe for API responses)."""
        d = self.to_dict()
        d.pop("password_hash", None)
        d["_id"] = self.id
        return d

    def deactivate(self) -> None:
        """Deactivate this user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate this user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def is_role(self, role: str) -> bool:
        """Check whether the user has the given role."""
        return self.role == role

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self._email} role={self.role}>"
