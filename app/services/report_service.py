"""
Report service — generates filtered reports and CSV exports.
"""
import csv
import io
from datetime import datetime
from typing import Optional
from app.extensions import get_db
from app.utils.helpers import serialize_doc, to_object_id


class ReportService:
    """Generates reports with optional filters and CSV download support."""

    @property
    def db(self):
        return get_db()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _date_filter(self, date_from: Optional[str], date_to: Optional[str], field: str) -> dict:
        f = {}
        try:
            if date_from:
                f.setdefault(field, {})["$gte"] = datetime.strptime(date_from, "%Y-%m-%d")
            if date_to:
                f.setdefault(field, {})["$lte"] = datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            pass
        return f

    # ------------------------------------------------------------------ #
    # Candidate report
    # ------------------------------------------------------------------ #
    def candidate_report(self, filters: dict = None) -> list:
        f = filters or {}
        query = {}
        query.update(self._date_filter(f.get("date_from"), f.get("date_to"), "created_at"))
        if f.get("location"):
            query["location"] = {"$regex": f["location"], "$options": "i"}
        docs = list(self.db.candidates.find(query).sort("created_at", -1))
        return [serialize_doc(d) for d in docs]

    # ------------------------------------------------------------------ #
    # Job report
    # ------------------------------------------------------------------ #
    def job_report(self, filters: dict = None) -> list:
        f = filters or {}
        query = {}
        query.update(self._date_filter(f.get("date_from"), f.get("date_to"), "posted_date"))
        if f.get("company_id"):
            query["company_id"] = to_object_id(f["company_id"])
        if f.get("location"):
            query["location"] = {"$regex": f["location"], "$options": "i"}
        if f.get("status"):
            query["status"] = f["status"]
        docs = list(self.db.jobs.find(query).sort("posted_date", -1))
        return [serialize_doc(d) for d in docs]

    # ------------------------------------------------------------------ #
    # Application report
    # ------------------------------------------------------------------ #
    def application_report(self, filters: dict = None) -> list:
        f = filters or {}
        query = {}
        query.update(self._date_filter(f.get("date_from"), f.get("date_to"), "applied_at"))
        if f.get("status"):
            query["status"] = f["status"]
        if f.get("job_id"):
            query["job_id"] = to_object_id(f["job_id"])
        docs = list(self.db.applications.find(query).sort("applied_at", -1))
        result = []
        for doc in docs:
            item = serialize_doc(doc)
            job = self.db.jobs.find_one({"_id": to_object_id(item.get("job_id", ""))})
            if job:
                item["job_title"] = job.get("title", "")
            candidate = self.db.candidates.find_one({"_id": to_object_id(item.get("candidate_id", ""))})
            if candidate:
                item["candidate_name"] = candidate.get("name", "")
                item["candidate_email"] = candidate.get("email", "")
            result.append(item)
        return result

    # ------------------------------------------------------------------ #
    # Skill demand report
    # ------------------------------------------------------------------ #
    def skill_demand_report(self) -> list:
        pipeline = [
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "job_count": {"$sum": 1}}},
            {"$sort": {"job_count": -1}},
        ]
        return list(self.db.jobs.aggregate(pipeline))

    # ------------------------------------------------------------------ #
    # CSV export helpers
    # ------------------------------------------------------------------ #
    def to_csv(self, records: list, columns: list) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in records:
            writer.writerow({col: row.get(col, "") for col in columns})
        return output.getvalue()

    def candidate_csv(self, filters: dict = None) -> str:
        records = self.candidate_report(filters)
        cols = ["_id", "name", "email", "phone", "location", "skills", "notice_period", "expected_salary", "created_at"]
        return self.to_csv(records, cols)

    def job_csv(self, filters: dict = None) -> str:
        records = self.job_report(filters)
        cols = ["_id", "title", "location", "work_mode", "employment_type", "status", "salary_min", "salary_max", "posted_date", "deadline"]
        return self.to_csv(records, cols)

    def application_csv(self, filters: dict = None) -> str:
        records = self.application_report(filters)
        cols = ["_id", "candidate_name", "candidate_email", "job_title", "status", "applied_at", "recruiter_notes"]
        return self.to_csv(records, cols)
