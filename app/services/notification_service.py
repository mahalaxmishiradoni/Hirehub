"""
Notification service — creates and manages in-app notifications.
"""
from app.repositories.notification_repository import NotificationRepository
from app.schemas.schemas import notification_schema
from app.utils.helpers import serialize_doc


class NotificationService:
    """Handles all notification business logic."""

    def __init__(self) -> None:
        self._repo = NotificationRepository()

    def create(self, user_id, title: str, message: str, notif_type: str = "GENERAL", resource_id=None) -> str:
        doc = notification_schema(user_id, title, message, notif_type, resource_id)
        inserted_id = self._repo.insert(doc)
        return str(inserted_id)

    def get_for_user(self, user_id, page: int = 1, per_page: int = 20) -> dict:
        result = self._repo.find_by_user(user_id, page, per_page)
        result["items"] = [serialize_doc(n) for n in result["items"]]
        return result

    def count_unread(self, user_id) -> int:
        return self._repo.count_unread(user_id)

    def mark_read(self, notif_id, user_id) -> bool:
        notif = self._repo.find_by_id(notif_id)
        if not notif or str(notif.get("user_id")) != str(user_id):
            return False
        return self._repo.mark_read(notif_id)

    def mark_all_read(self, user_id) -> int:
        return self._repo.mark_all_read(user_id)

    # --- Convenience factory methods for each notification event ---
    def notify_registration(self, user_id, name: str) -> None:
        self.create(user_id, "Welcome to HireHub!", f"Hi {name}, your account has been created.", "REGISTRATION")

    def notify_application_submitted(self, user_id, job_title: str, job_id=None) -> None:
        self.create(user_id, "Application Submitted", f"Your application for '{job_title}' has been submitted.", "APPLICATION_SUBMITTED", job_id)

    def notify_shortlisted(self, user_id, job_title: str, application_id=None) -> None:
        self.create(user_id, "You've Been Shortlisted!", f"Congratulations! You have been shortlisted for '{job_title}'.", "APPLICATION_SHORTLISTED", application_id)

    def notify_rejected(self, user_id, job_title: str, application_id=None) -> None:
        self.create(user_id, "Application Update", f"Thank you for your interest in '{job_title}'. We have decided to move forward with other candidates.", "APPLICATION_REJECTED", application_id)

    def notify_interview_scheduled(self, user_id, job_title: str, date: str, interview_id=None) -> None:
        self.create(user_id, "Interview Scheduled", f"Your interview for '{job_title}' has been scheduled on {date}.", "INTERVIEW_SCHEDULED", interview_id)

    def notify_interview_cancelled(self, user_id, job_title: str, interview_id=None) -> None:
        self.create(user_id, "Interview Cancelled", f"Your interview for '{job_title}' has been cancelled.", "INTERVIEW_CANCELLED", interview_id)

    def notify_selected(self, user_id, job_title: str, application_id=None) -> None:
        self.create(user_id, "Congratulations! You've Been Selected!", f"You have been selected for the position of '{job_title}'.", "CANDIDATE_SELECTED", application_id)
