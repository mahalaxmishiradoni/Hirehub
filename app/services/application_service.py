"""
Application service — apply, withdraw, status transitions.
"""
from datetime import datetime
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.company_repository import CompanyRepository
from app.schemas.schemas import application_schema
from app.utils.helpers import serialize_doc, to_object_id
from app.exceptions.app_exceptions import (
    JobNotFoundError, JobClosedError, DuplicateApplicationError,
    ApplicationNotFoundError, InvalidApplicationStatusError, UnauthorizedError,
)
from app.middleware.audit_middleware import AuditLogger
from app.services.notification_service import NotificationService


class ApplicationService:
    """Business logic for job applications."""

    def __init__(self) -> None:
        self._apps = ApplicationRepository()
        self._jobs = JobRepository()
        self._candidates = CandidateRepository()
        self._companies = CompanyRepository()
        self._notif = NotificationService()

    def apply(self, candidate_profile_id: str, user_id: str, job_id: str) -> dict:
        """Submit an application."""
        # Verify job exists and is open
        job = self._jobs.find_by_id(job_id)
        if not job:
            raise JobNotFoundError()
        if job.get("status") != "OPEN":
            raise JobClosedError()

        # Check deadline
        deadline = job.get("deadline")
        if deadline and isinstance(deadline, datetime) and datetime.utcnow() > deadline:
            raise JobClosedError("The application deadline has passed.")

        # Ownership check
        profile = self._candidates.find_by_id(candidate_profile_id)
        if not profile or str(profile.get("user_id")) != str(user_id):
            raise UnauthorizedError()

        # Duplicate check
        cid = to_object_id(candidate_profile_id)
        jid = to_object_id(job_id)
        if self._apps.find_by_candidate_and_job(cid, jid):
            raise DuplicateApplicationError()

        doc = application_schema(cid, jid)
        app_id = self._apps.insert(doc)

        AuditLogger.log(user_id, AuditLogger.APPLICATION_SUBMITTED, "applications", app_id)
        self._notif.notify_application_submitted(user_id, job.get("title", ""), jid)

        return serialize_doc(self._apps.find_by_id(app_id))

    def withdraw(self, application_id: str, user_id: str) -> dict:
        """Candidate withdraws their application."""
        app = self._apps.find_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError()

        # Ownership
        profile = self._candidates.find_by_user_id(user_id)
        if not profile or str(profile.get("_id")) != str(app.get("candidate_id")):
            raise UnauthorizedError()

        from app.models.application import Application
        app_model = Application.from_dict(app)
        app_model.withdraw()
        self._apps.update_status(application_id, "WITHDRAWN")
        return serialize_doc(self._apps.find_by_id(application_id))

    def update_status(self, application_id: str, new_status: str, recruiter_user_id: str, notes: str = "") -> dict:
        """Recruiter updates application status."""
        app = self._apps.find_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError()

        # Verify recruiter owns the job
        job = self._jobs.find_by_id(app.get("job_id"))
        if not job or str(job.get("recruiter_id")) != str(to_object_id(recruiter_user_id)):
            raise UnauthorizedError()

        from app.models.application import Application
        app_model = Application.from_dict(app)
        app_model.transition_to(new_status)  # raises InvalidApplicationStatusError if invalid

        self._apps.update_status(application_id, new_status, notes)

        # Fire notifications and audit events
        candidate_profile = self._candidates.find_by_id(app.get("candidate_id"))
        candidate_user_id = candidate_profile.get("user_id") if candidate_profile else None
        job_title = job.get("title", "")

        if new_status == "SHORTLISTED":
            AuditLogger.log(recruiter_user_id, AuditLogger.APPLICATION_SHORTLISTED, "applications", application_id)
            if candidate_user_id:
                self._notif.notify_shortlisted(candidate_user_id, job_title, application_id)

        elif new_status == "REJECTED":
            AuditLogger.log(recruiter_user_id, AuditLogger.APPLICATION_REJECTED, "applications", application_id)
            if candidate_user_id:
                self._notif.notify_rejected(candidate_user_id, job_title, application_id)

        elif new_status == "SELECTED":
            if candidate_user_id:
                self._notif.notify_selected(candidate_user_id, job_title, application_id)

        return serialize_doc(self._apps.find_by_id(application_id))

    def get_application(self, application_id: str, user_id: str, role: str) -> dict:
        app = self._apps.find_by_id(application_id)
        if not app:
            raise ApplicationNotFoundError()
        self._check_access(app, user_id, role)
        result = serialize_doc(app)
        # Enrich with job info
        job = self._jobs.find_by_id(app.get("job_id"))
        if job:
            result["job_title"] = job.get("title", "")
            result["job_location"] = job.get("location", "")
            result["job_status"] = job.get("status", "")
        return result

    def get_candidate_applications(self, candidate_profile_id: str, user_id: str, page: int = 1, per_page: int = 20) -> dict:
        profile = self._candidates.find_by_id(candidate_profile_id)
        if not profile or str(profile.get("user_id")) != str(user_id):
            raise UnauthorizedError()
        result = self._apps.find_by_candidate(to_object_id(candidate_profile_id), page, per_page)
        enriched = []
        for app in result["items"]:
            item = serialize_doc(app)
            job = self._jobs.find_by_id(app.get("job_id"))
            if job:
                item["job_title"] = job.get("title", "")
                item["job_location"] = job.get("location", "")
                item["job_status"] = job.get("status", "")
                company = self._companies.find_by_id(job.get("company_id"))
                if company:
                    item["company_name"] = company.get("name", "")
                    item["company_logo"] = company.get("logo_url", "")
            enriched.append(item)
        result["items"] = enriched
        return result

    def get_job_applications(self, job_id: str, recruiter_user_id: str, page: int = 1, per_page: int = 20) -> dict:
        job = self._jobs.find_by_id(job_id)
        if not job:
            raise JobNotFoundError()
        if str(job.get("recruiter_id")) != str(to_object_id(recruiter_user_id)):
            raise UnauthorizedError()
        result = self._apps.find_by_job(job_id, page, per_page)
        enriched = []
        for app in result["items"]:
            item = serialize_doc(app)
            profile = self._candidates.find_by_id(app.get("candidate_id"))
            if profile:
                item["candidate_name"] = profile.get("name", "")
                item["candidate_email"] = profile.get("email", "")
                item["candidate_skills"] = profile.get("skills", [])
                item["candidate_location"] = profile.get("location", "")
            enriched.append(item)
        result["items"] = enriched
        return result

    def get_all_applications(self, page: int = 1, per_page: int = 20) -> dict:
        """Admin: get all applications."""
        result = self._apps.find_all(page=page, per_page=per_page)
        result["items"] = [serialize_doc(a) for a in result["items"]]
        return result

    def _check_access(self, app: dict, user_id: str, role: str) -> None:
        if role == "ADMIN":
            return
        if role == "CANDIDATE":
            profile = self._candidates.find_by_user_id(user_id)
            if not profile or str(profile.get("_id")) != str(app.get("candidate_id")):
                raise UnauthorizedError()
        elif role == "RECRUITER":
            job = self._jobs.find_by_id(app.get("job_id"))
            if not job or str(job.get("recruiter_id")) != str(to_object_id(user_id)):
                raise UnauthorizedError()
