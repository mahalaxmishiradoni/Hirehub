"""
Interview service — schedule, update, cancel interviews.
"""
from app.repositories.interview_repository import InterviewRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.schemas import interview_schema
from app.utils.helpers import serialize_doc, to_object_id
from app.utils.validators import validate_date_string
from app.exceptions.app_exceptions import (
    InterviewNotFoundError, ApplicationNotFoundError, UnauthorizedError
)
from app.middleware.audit_middleware import AuditLogger
from app.services.notification_service import NotificationService


class InterviewService:
    """Business logic for interview scheduling."""

    def __init__(self) -> None:
        self._interviews = InterviewRepository()
        self._apps = ApplicationRepository()
        self._jobs = JobRepository()
        self._candidates = CandidateRepository()
        self._notif = NotificationService()

    def schedule_interview(self, application_id: str, recruiter_user_id: str, data: dict) -> dict:
        """Schedule an interview for an application."""
        app = self._apps.find_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError()

        job = self._jobs.find_by_id(app.get("job_id"))
        if not job or str(job.get("recruiter_id")) != str(to_object_id(recruiter_user_id)):
            raise UnauthorizedError()

        # Validate interview type
        valid_types = {"ONLINE", "PHONE", "IN_PERSON"}
        if data.get("type", "ONLINE").upper() not in valid_types:
            from app.exceptions.app_exceptions import ValidationError
            raise ValidationError(f"Interview type must be one of {valid_types}.", "type")

        # Validate date
        if data.get("date"):
            validate_date_string(data["date"], "date")

        data["type"] = data.get("type", "ONLINE").upper()

        rid = to_object_id(recruiter_user_id)
        cid = app.get("candidate_id")

        doc = interview_schema(data, to_object_id(application_id), cid, rid)
        interview_id = self._interviews.insert(doc)

        # Update application status and link interview
        self._apps.update_status(application_id, "INTERVIEW_SCHEDULED")
        self._apps.set_interview(application_id, interview_id)

        AuditLogger.log(recruiter_user_id, AuditLogger.INTERVIEW_SCHEDULED, "interviews", interview_id)

        # Notify candidate
        candidate_profile = self._candidates.find_by_id(cid)
        if candidate_profile:
            candidate_user_id = candidate_profile.get("user_id")
            self._notif.notify_interview_scheduled(
                candidate_user_id, job.get("title", ""),
                data.get("date", ""), interview_id
            )

        return serialize_doc(self._interviews.find_by_id(interview_id))

    def update_interview(self, interview_id: str, recruiter_user_id: str, data: dict) -> dict:
        interview = self._interviews.find_by_id(interview_id)
        if not interview:
            raise InterviewNotFoundError()
        if str(interview.get("recruiter_id")) != str(to_object_id(recruiter_user_id)):
            raise UnauthorizedError()

        allowed = ["date", "time", "type", "meeting_link", "status", "feedback"]
        update = {k: v for k, v in data.items() if k in allowed}
        self._interviews.update_by_id(interview_id, update)

        # Handle cancellation notifications
        if update.get("status") == "CANCELLED":
            candidate_profile = self._candidates.find_by_id(interview.get("candidate_id"))
            if candidate_profile:
                job_data = self._get_job_from_interview(interview)
                self._notif.notify_interview_cancelled(
                    candidate_profile.get("user_id"),
                    job_data.get("title", ""),
                    interview_id
                )

        return serialize_doc(self._interviews.find_by_id(interview_id))

    def get_interview(self, interview_id: str, user_id: str, role: str) -> dict:
        interview = self._interviews.find_by_id(interview_id)
        if not interview:
            raise InterviewNotFoundError()
        self._check_access(interview, user_id, role)
        return serialize_doc(interview)

    def get_candidate_interviews(self, candidate_profile_id: str, user_id: str, page: int = 1, per_page: int = 20) -> dict:
        profile = self._candidates.find_by_id(candidate_profile_id)
        if not profile or str(profile.get("user_id")) != str(user_id):
            raise UnauthorizedError()
        result = self._interviews.find_by_candidate(to_object_id(candidate_profile_id), page, per_page)
        enriched = []
        for iv in result["items"]:
            item = serialize_doc(iv)
            app = self._apps.find_by_id(iv.get("application_id"))
            if app:
                job = self._jobs.find_by_id(app.get("job_id"))
                if job:
                    item["job_title"] = job.get("title", "")
                    item["company_id"] = str(job.get("company_id", ""))
            enriched.append(item)
        result["items"] = enriched
        return result

    def get_recruiter_interviews(self, recruiter_user_id: str, page: int = 1, per_page: int = 20) -> dict:
        oid = to_object_id(recruiter_user_id)
        result = self._interviews.find_by_recruiter(oid, page, per_page)
        enriched = []
        for iv in result["items"]:
            item = serialize_doc(iv)
            candidate = self._candidates.find_by_id(iv.get("candidate_id"))
            if candidate:
                item["candidate_name"] = candidate.get("name", "")
            enriched.append(item)
        result["items"] = enriched
        return result

    def _check_access(self, interview: dict, user_id: str, role: str) -> None:
        if role == "ADMIN":
            return
        if role == "CANDIDATE":
            profile = self._candidates.find_by_user_id(user_id)
            if not profile or str(profile.get("_id")) != str(interview.get("candidate_id")):
                raise UnauthorizedError()
        elif role == "RECRUITER":
            if str(interview.get("recruiter_id")) != str(to_object_id(user_id)):
                raise UnauthorizedError()

    def _get_job_from_interview(self, interview: dict) -> dict:
        app = self._apps.find_by_id(interview.get("application_id"))
        if app:
            job = self._jobs.find_by_id(app.get("job_id"))
            return job or {}
        return {}
