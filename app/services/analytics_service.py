"""
Analytics service — aggregated statistics and chart data.
"""
from app.repositories.analytics_repository import AnalyticsRepository
from app.utils.helpers import serialize_doc


class AnalyticsService:
    """Wraps AnalyticsRepository and formats data for Chart.js."""

    def __init__(self) -> None:
        self._repo = AnalyticsRepository()

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _month_label(m: int) -> str:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return months[m - 1] if 1 <= m <= 12 else str(m)

    @staticmethod
    def _fill_months(data: list, key: str = "_id") -> dict:
        """Expand sparse monthly data to all 12 months."""
        lookup = {r[key]: r["count"] for r in data}
        return {
            "labels": [AnalyticsService._month_label(i) for i in range(1, 13)],
            "data": [lookup.get(i, 0) for i in range(1, 13)],
        }

    # ------------------------------------------------------------------ #
    # Admin analytics
    # ------------------------------------------------------------------ #
    def get_admin_overview(self) -> dict:
        return self._repo.admin_overview()

    def get_jobs_by_skill(self, limit: int = 15) -> dict:
        raw = self._repo.jobs_by_skill(limit)
        return {
            "labels": [r["_id"] for r in raw],
            "data": [r["count"] for r in raw],
        }

    def get_jobs_by_location(self) -> dict:
        raw = self._repo.jobs_by_location()
        return {
            "labels": [r["_id"] for r in raw],
            "data": [r["count"] for r in raw],
        }

    def get_jobs_by_work_mode(self) -> dict:
        raw = self._repo.jobs_by_work_mode()
        return {
            "labels": [r["_id"] for r in raw],
            "data": [r["count"] for r in raw],
        }

    def get_applications_by_status(self) -> dict:
        raw = self._repo.applications_by_status()
        return {
            "labels": [r["_id"] for r in raw],
            "data": [r["count"] for r in raw],
        }

    def get_monthly_applications(self, year: int = None) -> dict:
        raw = self._repo.monthly_applications(year)
        return self._fill_months(raw)

    def get_monthly_registrations(self, year: int = None) -> dict:
        raw = self._repo.monthly_registrations(year)
        # Group by month, sum all roles
        monthly: dict = {}
        for r in raw:
            month = r["_id"]["month"]
            monthly[month] = monthly.get(month, 0) + r["count"]
        return {
            "labels": [self._month_label(i) for i in range(1, 13)],
            "data": [monthly.get(i, 0) for i in range(1, 13)],
        }

    def get_top_skills(self, limit: int = 10) -> dict:
        return self.get_jobs_by_skill(limit)

    def get_applications_by_company(self, limit: int = 10) -> dict:
        raw = self._repo.applications_by_company(limit)
        return {
            "labels": [r["_id"] for r in raw],
            "data": [r["count"] for r in raw],
        }

    # ------------------------------------------------------------------ #
    # Recruiter analytics
    # ------------------------------------------------------------------ #
    def get_recruiter_stats(self, recruiter_user_id: str) -> dict:
        return self._repo.recruiter_stats(recruiter_user_id)

    # ------------------------------------------------------------------ #
    # Candidate analytics
    # ------------------------------------------------------------------ #
    def get_candidate_stats(self, candidate_profile_id: str) -> dict:
        return self._repo.candidate_stats(candidate_profile_id)
