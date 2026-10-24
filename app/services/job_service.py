"""
Job service — creation, editing, search, filtering.
"""
from datetime import datetime
from app.repositories.job_repository import JobRepository
from app.repositories.company_repository import CompanyRepository
from app.schemas.schemas import job_schema
from app.utils.helpers import serialize_doc, to_object_id
from app.utils.validators import validate_job
from app.exceptions.app_exceptions import JobNotFoundError, UnauthorizedError
from app.middleware.audit_middleware import AuditLogger


class JobService:
    """Business logic for job postings."""

    def __init__(self) -> None:
        self._jobs = JobRepository()
        self._companies = CompanyRepository()

    def create_job(self, data: dict, recruiter_user_id: str, company_id: str) -> dict:
        validate_job(data)

        # Parse skills from comma-separated string if needed
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip().lower() for s in skills.split(",") if s.strip()]
        data["skills"] = skills

        # Handle deadline
        deadline = data.get("deadline")
        if deadline and isinstance(deadline, str):
            try:
                data["deadline"] = datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                data["deadline"] = None

        rid = to_object_id(recruiter_user_id)
        cid = to_object_id(company_id)
        doc = job_schema(data, rid, cid)
        job_id = self._jobs.insert(doc)

        AuditLogger.log(recruiter_user_id, AuditLogger.JOB_CREATED, "jobs", job_id, {"title": data.get("title")})
        return serialize_doc(self._jobs.find_by_id(job_id))

    def get_job(self, job_id: str) -> dict:
        doc = self._jobs.find_by_id(job_id)
        if not doc:
            raise JobNotFoundError()
        result = serialize_doc(doc)
        # Attach company info
        if doc.get("company_id"):
            company = self._companies.find_by_id(doc["company_id"])
            if company:
                result["company_name"] = company.get("name", "")
                result["company_location"] = company.get("location", "")
                result["company_logo"] = company.get("logo_url", "")
        return result

    def update_job(self, job_id: str, recruiter_user_id: str, data: dict) -> dict:
        doc = self._jobs.find_by_id(job_id)
        if not doc:
            raise JobNotFoundError()
        if str(doc.get("recruiter_id")) != str(to_object_id(recruiter_user_id)):
            raise UnauthorizedError()

        validate_job(data)
        allowed = [
            "title", "description", "skills", "location", "work_mode",
            "employment_type", "experience_min", "experience_max",
            "salary_min", "salary_max", "deadline",
        ]
        update = {k: v for k, v in data.items() if k in allowed}

        if "skills" in update and isinstance(update["skills"], str):
            update["skills"] = [s.strip().lower() for s in update["skills"].split(",") if s.strip()]

        if "deadline" in update and isinstance(update["deadline"], str):
            try:
                update["deadline"] = datetime.strptime(update["deadline"], "%Y-%m-%d")
            except ValueError:
                update.pop("deadline")

        self._jobs.update_by_id(job_id, update)
        AuditLogger.log(recruiter_user_id, AuditLogger.JOB_UPDATED, "jobs", job_id)
        return self.get_job(job_id)

    def close_job(self, job_id: str, recruiter_user_id: str) -> dict:
        doc = self._jobs.find_by_id(job_id)
        if not doc:
            raise JobNotFoundError()
        if str(doc.get("recruiter_id")) != str(to_object_id(recruiter_user_id)):
            raise UnauthorizedError()
        self._jobs.close_job(job_id)
        AuditLogger.log(recruiter_user_id, AuditLogger.JOB_CLOSED, "jobs", job_id)
        return self.get_job(job_id)

    def delete_job(self, job_id: str, recruiter_user_id: str) -> bool:
        doc = self._jobs.find_by_id(job_id)
        if not doc:
            raise JobNotFoundError()
        if str(doc.get("recruiter_id")) != str(to_object_id(recruiter_user_id)):
            raise UnauthorizedError()
        return self._jobs.delete_by_id(job_id)

    def search_jobs(self, filters: dict, page: int = 1, per_page: int = 10) -> dict:
        skills_raw = filters.get("skills", "")
        skills = [s.strip().lower() for s in skills_raw.split(",") if s.strip()] if isinstance(skills_raw, str) else skills_raw

        result = self._jobs.search(
            keyword=filters.get("keyword", ""),
            skills=skills,
            location=filters.get("location", ""),
            salary_min=float(filters["salary_min"]) if filters.get("salary_min") else None,
            salary_max=float(filters["salary_max"]) if filters.get("salary_max") else None,
            experience_min=int(filters["experience_min"]) if filters.get("experience_min") else None,
            experience_max=int(filters["experience_max"]) if filters.get("experience_max") else None,
            work_mode=filters.get("work_mode", ""),
            employment_type=filters.get("employment_type", ""),
            company_id=filters.get("company_id"),
            status=filters.get("status", "OPEN"),
            page=page,
            per_page=per_page,
        )
        enriched = []
        for doc in result["items"]:
            item = serialize_doc(doc)
            if doc.get("company_id"):
                company = self._companies.find_by_id(doc["company_id"])
                if company:
                    item["company_name"] = company.get("name", "")
                    item["company_logo"] = company.get("logo_url", "")
            enriched.append(item)
        result["items"] = enriched
        return result

    def get_recruiter_jobs(self, recruiter_user_id: str, page: int = 1, per_page: int = 10) -> dict:
        oid = to_object_id(recruiter_user_id)
        result = self._jobs.find_by_recruiter(oid, page, per_page)
        result["items"] = [serialize_doc(d) for d in result["items"]]
        return result

    def get_open_jobs(self, limit: int = 100) -> list:
        return [serialize_doc(d) for d in self._jobs.find_open_jobs(limit)]
