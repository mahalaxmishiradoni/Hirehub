"""
Create MongoDB indexes for HireHub.
Run once after setting up the database.

Usage:
    python scripts/create_indexes.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB  = os.environ.get("MONGO_DATABASE", "hirehub")

client = MongoClient(MONGO_URI)
db     = client[MONGO_DB]


def create_indexes():
    print(f"Connected to: {MONGO_URI}  database: {MONGO_DB}\n")

    # ── users ──────────────────────────────────────────────────────────────
    db.users.create_index([("email", ASCENDING)], unique=True, name="users_email_unique")
    db.users.create_index([("role",  ASCENDING)], name="users_role")
    db.users.create_index([("is_active", ASCENDING)], name="users_is_active")
    print("✓  users indexes created")

    # ── candidates ─────────────────────────────────────────────────────────
    db.candidates.create_index([("user_id", ASCENDING)], unique=True, name="candidates_user_id_unique")
    db.candidates.create_index([("skills", ASCENDING)], name="candidates_skills")
    db.candidates.create_index([("location", ASCENDING)], name="candidates_location")
    print("✓  candidates indexes created")

    # ── recruiters ─────────────────────────────────────────────────────────
    db.recruiters.create_index([("user_id",    ASCENDING)], unique=True, name="recruiters_user_id_unique")
    db.recruiters.create_index([("company_id", ASCENDING)], name="recruiters_company_id")
    print("✓  recruiters indexes created")

    # ── companies ──────────────────────────────────────────────────────────
    db.companies.create_index([("name", ASCENDING)], name="companies_name")
    db.companies.create_index([("is_verified", ASCENDING)], name="companies_verified")
    print("✓  companies indexes created")

    # ── jobs ───────────────────────────────────────────────────────────────
    db.jobs.create_index([("title",  TEXT), ("description", TEXT)], name="jobs_text_search")
    db.jobs.create_index([("skills", ASCENDING)], name="jobs_skills")
    db.jobs.create_index([("location", ASCENDING)], name="jobs_location")
    db.jobs.create_index([("status", ASCENDING)], name="jobs_status")
    db.jobs.create_index([("recruiter_id", ASCENDING)], name="jobs_recruiter_id")
    db.jobs.create_index([("company_id",   ASCENDING)], name="jobs_company_id")
    db.jobs.create_index([("posted_date",  DESCENDING)], name="jobs_posted_date")
    db.jobs.create_index([("work_mode", ASCENDING)], name="jobs_work_mode")
    db.jobs.create_index([("employment_type", ASCENDING)], name="jobs_employment_type")
    print("✓  jobs indexes created")

    # ── applications ───────────────────────────────────────────────────────
    db.applications.create_index(
        [("candidate_id", ASCENDING), ("job_id", ASCENDING)],
        unique=True,
        name="applications_candidate_job_unique",
    )
    db.applications.create_index([("candidate_id", ASCENDING)], name="applications_candidate_id")
    db.applications.create_index([("job_id",        ASCENDING)], name="applications_job_id")
    db.applications.create_index([("status",        ASCENDING)], name="applications_status")
    db.applications.create_index([("applied_at",    DESCENDING)], name="applications_applied_at")
    print("✓  applications indexes created")

    # ── interviews ─────────────────────────────────────────────────────────
    db.interviews.create_index([("application_id", ASCENDING)], name="interviews_application_id")
    db.interviews.create_index([("candidate_id",   ASCENDING)], name="interviews_candidate_id")
    db.interviews.create_index([("recruiter_id",   ASCENDING)], name="interviews_recruiter_id")
    db.interviews.create_index([("date", ASCENDING)], name="interviews_date")
    print("✓  interviews indexes created")

    # ── resumes ────────────────────────────────────────────────────────────
    db.resumes.create_index([("candidate_id", ASCENDING)], name="resumes_candidate_id")
    print("✓  resumes indexes created")

    # ── notifications ──────────────────────────────────────────────────────
    db.notifications.create_index([("user_id",    ASCENDING)], name="notifications_user_id")
    db.notifications.create_index([("is_read",    ASCENDING)], name="notifications_is_read")
    db.notifications.create_index([("created_at", DESCENDING)], name="notifications_created_at")
    print("✓  notifications indexes created")

    # ── audit_logs ─────────────────────────────────────────────────────────
    db.audit_logs.create_index([("user_id",   ASCENDING)],  name="audit_logs_user_id")
    db.audit_logs.create_index([("action",    ASCENDING)],  name="audit_logs_action")
    db.audit_logs.create_index([("timestamp", DESCENDING)], name="audit_logs_timestamp")
    print("✓  audit_logs indexes created")

    print("\nAll indexes created successfully.")
    client.close()


if __name__ == "__main__":
    create_indexes()
