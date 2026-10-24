"""
Job repository — CRUD + search/filter against the `jobs` collection.
"""
from typing import Optional, Any, List
from bson import ObjectId
from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class JobRepository(BaseRepository):
    collection_name = "jobs"

    def find_by_id(self, doc_id: Any) -> Optional[dict]:
        oid = to_object_id(doc_id)
        return self.collection.find_one({"_id": oid}) if oid else None

    def find_all(self, filters: dict = None, page: int = 1, per_page: int = 10) -> dict:
        query = filters or {}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("posted_date", -1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_recruiter(self, recruiter_id: Any, page: int = 1, per_page: int = 10) -> dict:
        oid = to_object_id(recruiter_id)
        query = {"recruiter_id": oid}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("posted_date", -1)
        return self._paginate(cursor, page, per_page, total)

    def find_by_company(self, company_id: Any, page: int = 1, per_page: int = 10) -> dict:
        oid = to_object_id(company_id)
        query = {"company_id": oid, "status": "OPEN"}
        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("posted_date", -1)
        return self._paginate(cursor, page, per_page, total)

    def search(
        self,
        keyword: str = "",
        skills: List[str] = None,
        location: str = "",
        salary_min: float = None,
        salary_max: float = None,
        experience_min: int = None,
        experience_max: int = None,
        work_mode: str = "",
        employment_type: str = "",
        company_id: Any = None,
        status: str = "OPEN",
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        """Flexible job search with multiple optional filters."""
        query: dict = {}

        if status:
            query["status"] = status

        if keyword:
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
            ]

        if skills:
            lower_skills = [s.lower().strip() for s in skills if s.strip()]
            if lower_skills:
                query["skills"] = {"$elemMatch": {"$in": lower_skills}}

        if location:
            query["location"] = {"$regex": location, "$options": "i"}

        if work_mode:
            query["work_mode"] = work_mode.upper()

        if employment_type:
            query["employment_type"] = employment_type.upper()

        if salary_min is not None:
            query.setdefault("salary_max", {})["$gte"] = salary_min

        if salary_max is not None:
            query.setdefault("salary_min", {})["$lte"] = salary_max

        if experience_min is not None:
            query["experience_max"] = {"$gte": experience_min}

        if experience_max is not None:
            query["experience_min"] = {"$lte": experience_max}

        if company_id:
            query["company_id"] = to_object_id(company_id)

        total = self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("posted_date", -1)
        return self._paginate(cursor, page, per_page, total)

    def close_job(self, job_id: Any) -> bool:
        return self.update_by_id(job_id, {"status": "CLOSED"})

    def find_open_jobs(self, limit: int = 100) -> List[dict]:
        return list(self.collection.find({"status": "OPEN"}).sort("posted_date", -1).limit(limit))
