"""
Candidate service — profile management, saved jobs.
"""
from datetime import datetime
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.user_repository import UserRepository
from app.utils.helpers import serialize_doc, to_object_id, calculate_profile_completion
from app.exceptions.app_exceptions import UserNotFoundError, UnauthorizedError


def _normalise_list_of_dicts(value: list) -> list:
    """
    Ensure every element of a list is a dict.

    Handles three cases that can arrive from user input or legacy DB data:
    - Already a dict          → kept as-is
    - A plain string          → wrapped as {"value": str}  so the template can
                                render it gracefully rather than crash on .get()
    - Anything else (None, …) → skipped entirely
    """
    result = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
        elif isinstance(item, str) and item.strip():
            result.append({"value": item.strip()})
        # silently drop None / empty strings / other types
    return result


def _normalise_profile(profile: dict) -> dict:
    """
    Coerce experience and education lists so that every element is a dict.
    Applied both on read (safety for legacy data) and on write (prevent future issues).
    """
    for field in ("experience", "education"):
        raw = profile.get(field)
        if isinstance(raw, list):
            profile[field] = _normalise_list_of_dicts(raw)
        elif raw is None:
            profile[field] = []
    # Skills must be a list of strings
    skills = profile.get("skills")
    if not isinstance(skills, list):
        profile["skills"] = []
    return profile


class CandidateService:
    """Business logic for candidate profiles."""

    def __init__(self) -> None:
        self._candidates = CandidateRepository()
        self._users = UserRepository()

    def get_profile(self, candidate_profile_id: str) -> dict:
        doc = self._candidates.find_by_id(candidate_profile_id)
        if not doc:
            raise UserNotFoundError("Candidate profile not found.")
        result = serialize_doc(doc)
        result = _normalise_profile(result)
        result["profile_completion"] = calculate_profile_completion(result)
        return result

    def get_profile_by_user_id(self, user_id: str) -> dict:
        doc = self._candidates.find_by_user_id(user_id)
        if not doc:
            raise UserNotFoundError("Candidate profile not found.")
        result = serialize_doc(doc)
        result = _normalise_profile(result)
        result["profile_completion"] = calculate_profile_completion(result)
        return result

    def update_profile(self, candidate_profile_id: str, user_id: str, data: dict) -> dict:
        """Update candidate profile; enforces ownership."""
        doc = self._candidates.find_by_id(candidate_profile_id)
        if not doc:
            raise UserNotFoundError("Profile not found.")
        if str(doc.get("user_id")) != str(user_id):
            raise UnauthorizedError()

        allowed_fields = [
            "name", "phone", "location", "skills", "education",
            "experience", "expected_salary", "notice_period",
        ]
        update = {k: v for k, v in data.items() if k in allowed_fields}

        # Normalise skills to lowercase stripped list
        if "skills" in update:
            update["skills"] = [s.strip().lower() for s in update["skills"] if isinstance(s, str) and s.strip()]

        # Normalise experience: every element must be a dict; strings are wrapped
        if "experience" in update:
            update["experience"] = _normalise_list_of_dicts(update["experience"])

        # Normalise education: same rule
        if "education" in update:
            update["education"] = _normalise_list_of_dicts(update["education"])

        self._candidates.update_by_id(candidate_profile_id, update)

        # Also update name in users collection if changed
        if "name" in update:
            self._users.update_by_id(user_id, {"name": update["name"]})

        return self.get_profile(candidate_profile_id)

    def save_job(self, candidate_profile_id: str, user_id: str, job_id: str) -> bool:
        doc = self._candidates.find_by_id(candidate_profile_id)
        if not doc or str(doc.get("user_id")) != str(user_id):
            raise UnauthorizedError()
        return self._candidates.add_saved_job(candidate_profile_id, job_id)

    def unsave_job(self, candidate_profile_id: str, user_id: str, job_id: str) -> bool:
        doc = self._candidates.find_by_id(candidate_profile_id)
        if not doc or str(doc.get("user_id")) != str(user_id):
            raise UnauthorizedError()
        return self._candidates.remove_saved_job(candidate_profile_id, job_id)

    def get_saved_jobs(self, candidate_profile_id: str) -> list:
        doc = self._candidates.find_by_id(candidate_profile_id)
        if not doc:
            return []
        return [str(j) for j in doc.get("saved_jobs", [])]

    def search_candidates(self, skills: list = None, page: int = 1, per_page: int = 20) -> dict:
        if skills:
            result = self._candidates.search_by_skills(skills, page, per_page)
        else:
            result = self._candidates.find_all(page=page, per_page=per_page)
        result["items"] = [serialize_doc(c) for c in result["items"]]
        return result

    def list_all(self, page: int = 1, per_page: int = 20) -> dict:
        result = self._candidates.find_all(page=page, per_page=per_page)
        result["items"] = [serialize_doc(c) for c in result["items"]]
        return result
