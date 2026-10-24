"""
Audit logging middleware / helper used by services.
"""
from datetime import datetime
from app.extensions import get_db
from app.schemas.schemas import audit_log_schema


class AuditLogger:
    """Records user actions into the audit_logs collection."""

    # Action constants
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    JOB_CREATED = "JOB_CREATED"
    JOB_UPDATED = "JOB_UPDATED"
    JOB_CLOSED = "JOB_CLOSED"
    APPLICATION_SUBMITTED = "APPLICATION_SUBMITTED"
    APPLICATION_SHORTLISTED = "APPLICATION_SHORTLISTED"
    APPLICATION_REJECTED = "APPLICATION_REJECTED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    RESUME_UPLOADED = "RESUME_UPLOADED"
    USER_DEACTIVATED = "USER_DEACTIVATED"

    @staticmethod
    def log(user_id, action: str, resource: str, resource_id=None, metadata: dict = None) -> None:
        """Insert an audit log entry. Never logs secrets or passwords."""
        try:
            db = get_db()
            entry = audit_log_schema(user_id, action, resource, resource_id, metadata)
            db.audit_logs.insert_one(entry)
        except Exception:
            pass  # Audit logging must never break core functionality

    @staticmethod
    def get_logs(page: int = 1, per_page: int = 50, filters: dict = None) -> dict:
        """Return paginated audit logs."""
        db = get_db()
        query = filters or {}
        total = db.audit_logs.count_documents(query)
        skip = (page - 1) * per_page
        logs = list(db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(per_page))
        return {
            "items": logs,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        }
