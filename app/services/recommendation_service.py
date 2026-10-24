"""
Recommendation service — returns top-matched jobs for a candidate.
"""
from app.repositories.job_repository import JobRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.company_repository import CompanyRepository
from app.services.matching_service import MatchingService
from app.utils.helpers import serialize_doc
from app.exceptions.app_exceptions import UserNotFoundError


class RecommendationService:
    """Returns recommended jobs for a candidate sorted by match score."""

    def __init__(self) -> None:
        self._jobs = JobRepository()
        self._candidates = CandidateRepository()
        self._companies = CompanyRepository()
        self._matcher = MatchingService()

    def get_recommendations(self, candidate_profile_id: str, limit: int = 10) -> list:
        """
        Return top `limit` open jobs ranked by match score for the candidate.
        """
        profile = self._candidates.find_by_id(candidate_profile_id)
        if not profile:
            raise UserNotFoundError("Candidate profile not found.")

        candidate = serialize_doc(profile)
        open_jobs = self._jobs.find_open_jobs(limit=100)

        ranked = MatchingService.rank_jobs(candidate, [serialize_doc(j) for j in open_jobs])

        # Enrich with company details
        top = ranked[:limit]
        for job in top:
            if job.get("company_id"):
                company = self._companies.find_by_id(job["company_id"])
                if company:
                    job["company_name"] = company.get("name", "")
                    job["company_location"] = company.get("location", "")
                    job["company_logo"] = company.get("logo_url", "")

        return top
