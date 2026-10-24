"""
Recruiter service — profile management.
"""
from app.repositories.recruiter_repository import RecruiterRepository
from app.repositories.user_repository import UserRepository
from app.utils.helpers import serialize_doc
from app.exceptions.app_exceptions import UserNotFoundError, UnauthorizedError


class RecruiterService:
    """Business logic for recruiter profiles."""

    def __init__(self) -> None:
        self._recruiters = RecruiterRepository()
        self._users = UserRepository()

    def get_profile(self, recruiter_profile_id: str) -> dict:
        doc = self._recruiters.find_by_id(recruiter_profile_id)
        if not doc:
            raise UserNotFoundError("Recruiter profile not found.")
        return serialize_doc(doc)

    def get_profile_by_user_id(self, user_id: str) -> dict:
        doc = self._recruiters.find_by_user_id(user_id)
        if not doc:
            raise UserNotFoundError("Recruiter profile not found.")
        return serialize_doc(doc)

    def update_profile(self, recruiter_profile_id: str, user_id: str, data: dict) -> dict:
        doc = self._recruiters.find_by_id(recruiter_profile_id)
        if not doc:
            raise UserNotFoundError("Profile not found.")
        if str(doc.get("user_id")) != str(user_id):
            raise UnauthorizedError()

        allowed = ["name", "phone"]
        update = {k: v for k, v in data.items() if k in allowed}
        self._recruiters.update_by_id(recruiter_profile_id, update)

        if "name" in update:
            self._users.update_by_id(user_id, {"name": update["name"]})

        return self.get_profile(recruiter_profile_id)

    def list_all(self, page: int = 1, per_page: int = 20) -> dict:
        result = self._recruiters.find_all(page=page, per_page=per_page)
        result["items"] = [serialize_doc(r) for r in result["items"]]
        return result
