"""
Authentication service — registration, login, logout.
"""
from datetime import datetime
from flask import session
from app.repositories.user_repository import UserRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.recruiter_repository import RecruiterRepository
from app.repositories.company_repository import CompanyRepository
from app.models.user import User
from app.schemas.schemas import user_schema, candidate_schema, recruiter_schema, company_schema
from app.utils.validators import validate_registration
from app.utils.helpers import serialize_doc, to_object_id
from app.exceptions.app_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.middleware.audit_middleware import AuditLogger
from app.services.notification_service import NotificationService


class AuthService:
    """Handles user registration, login, and session management."""

    def __init__(self) -> None:
        self._users = UserRepository()
        self._candidates = CandidateRepository()
        self._recruiters = RecruiterRepository()
        self._companies = CompanyRepository()
        self._notif = NotificationService()

    def register_candidate(self, data: dict) -> dict:
        """Register a new candidate."""
        validate_registration(data, role="CANDIDATE")
        email = data["email"].lower().strip()

        if self._users.email_exists(email):
            raise UserAlreadyExistsError()

        pwd_hash = User.hash_password(data["password"])
        user_doc = user_schema(data["name"], email, data["phone"], pwd_hash, "CANDIDATE")
        user_id = self._users.insert(user_doc)

        profile_doc = candidate_schema(user_id, data["name"], email)
        profile_doc["phone"] = data["phone"].strip()
        self._candidates.insert(profile_doc)

        AuditLogger.log(user_id, AuditLogger.USER_REGISTERED, "users", user_id, {"role": "CANDIDATE"})
        self._notif.notify_registration(user_id, data["name"])

        return {"user_id": str(user_id), "role": "CANDIDATE"}

    def register_recruiter(self, data: dict) -> dict:
        """Register a new recruiter and create their company."""
        validate_registration(data, role="RECRUITER")
        email = data["email"].lower().strip()

        if self._users.email_exists(email):
            raise UserAlreadyExistsError()

        pwd_hash = User.hash_password(data["password"])
        user_doc = user_schema(data["name"], email, data["phone"], pwd_hash, "RECRUITER")
        user_id = self._users.insert(user_doc)

        # Create company
        company_doc = company_schema(data["company_name"], user_id)
        company_id = self._companies.insert(company_doc)

        # Create recruiter profile
        recruiter_doc = recruiter_schema(user_id, data["name"], email, company_id)
        recruiter_doc["phone"] = data["phone"].strip()
        self._recruiters.insert(recruiter_doc)

        AuditLogger.log(user_id, AuditLogger.USER_REGISTERED, "users", user_id, {"role": "RECRUITER"})
        self._notif.notify_registration(user_id, data["name"])

        return {"user_id": str(user_id), "role": "RECRUITER"}

    def login(self, email: str, password: str) -> dict:
        """Authenticate a user and populate the Flask session."""
        user_doc = self._users.find_by_email(email)
        if not user_doc:
            raise InvalidCredentialsError()
        if not user_doc.get("is_active", True):
            raise InvalidCredentialsError("Your account has been deactivated.")
        if not User.verify_password(password, user_doc["password_hash"]):
            raise InvalidCredentialsError()

        user = User.from_dict(user_doc)

        # Build session
        from flask import current_app
        session.permanent = not current_app.config.get("TESTING", False)
        session["user_id"] = str(user.id)
        session["email"] = user.email
        session["name"] = user.name
        session["role"] = user.role

        # Attach profile id for role-specific profile lookups
        if user.role == "CANDIDATE":
            profile = self._candidates.find_by_user_id(user.id)
            if profile:
                session["profile_id"] = str(profile["_id"])
        elif user.role == "RECRUITER":
            profile = self._recruiters.find_by_user_id(user.id)
            if profile:
                session["profile_id"] = str(profile["_id"])
                session["company_id"] = str(profile.get("company_id", ""))

        AuditLogger.log(user.id, AuditLogger.USER_LOGIN, "users", user.id)

        return serialize_doc(user.to_safe_dict())

    def logout(self) -> None:
        """Clear the Flask session."""
        user_id = session.get("user_id")
        AuditLogger.log(user_id, AuditLogger.USER_LOGOUT, "users", user_id)
        session.clear()

    def get_current_user(self) -> dict:
        """Return the currently logged-in user's safe dict."""
        user_id = session.get("user_id")
        if not user_id:
            raise UserNotFoundError("No user is logged in.")
        user_doc = self._users.find_by_id(user_id)
        if not user_doc:
            raise UserNotFoundError()
        user = User.from_dict(user_doc)
        return serialize_doc(user.to_safe_dict())
