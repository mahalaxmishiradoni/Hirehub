"""
Resume service — upload, download, delete with full validation.
"""
import os
from flask import current_app
from werkzeug.utils import secure_filename
from app.repositories.resume_repository import ResumeRepository
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.schemas import resume_schema
from app.utils.helpers import generate_unique_filename, serialize_doc, to_object_id
from app.utils.validators import validate_file_upload
from app.exceptions.app_exceptions import ResumeUploadError, UnauthorizedError, UserNotFoundError
from app.middleware.audit_middleware import AuditLogger


class ResumeService:
    """Handles resume upload, retrieval and deletion."""

    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
    ALLOWED_MIMETYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    def __init__(self) -> None:
        self._resumes = ResumeRepository()
        self._candidates = CandidateRepository()

    def upload_resume(self, file, candidate_profile_id: str, user_id: str) -> dict:
        """Upload or replace the candidate's resume."""
        # Ownership check
        profile = self._candidates.find_by_id(candidate_profile_id)
        if not profile:
            raise UserNotFoundError("Candidate profile not found.")
        if str(profile.get("user_id")) != str(user_id):
            raise UnauthorizedError()

        if not file or not file.filename:
            raise ResumeUploadError("No file provided.")

        original_filename = file.filename
        max_size = current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)

        # Read content to validate size
        file_content = file.read()
        file_size = len(file_content)

        validate_file_upload(original_filename, file_size, max_size, self.ALLOWED_EXTENSIONS)

        # Delete existing resume if any
        existing_id = profile.get("resume_id")
        if existing_id:
            self._delete_resume_file(existing_id)

        # Generate safe unique filename
        stored_filename = generate_unique_filename(secure_filename(original_filename))
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, stored_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        doc = resume_schema(to_object_id(candidate_profile_id), original_filename, stored_filename, file_size)
        resume_id = self._resumes.insert(doc)

        # Update candidate profile with resume reference
        self._candidates.update_resume(candidate_profile_id, resume_id)

        AuditLogger.log(user_id, AuditLogger.RESUME_UPLOADED, "resumes", resume_id)

        return serialize_doc(self._resumes.find_by_id(resume_id))

    def get_resume(self, resume_id: str, requester_user_id: str, requester_role: str) -> dict:
        """Return resume metadata; enforces authorisation."""
        doc = self._resumes.find_by_id(resume_id)
        if not doc:
            raise UserNotFoundError("Resume not found.")

        # Candidates can only access their own resume; recruiters and admins can access any
        if requester_role == "CANDIDATE":
            profile = self._candidates.find_by_user_id(requester_user_id)
            if not profile or str(profile.get("_id")) != str(doc.get("candidate_id")):
                raise UnauthorizedError()

        return serialize_doc(doc)

    def get_file_path(self, resume_id: str, requester_user_id: str, requester_role: str) -> str:
        """Return the full file path for serving/downloading."""
        doc = self.get_resume(resume_id, requester_user_id, requester_role)
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        return os.path.join(upload_folder, doc["stored_filename"])

    def delete_resume(self, resume_id: str, user_id: str) -> bool:
        doc = self._resumes.find_by_id(resume_id)
        if not doc:
            return False
        profile = self._candidates.find_by_id(doc.get("candidate_id"))
        if not profile or str(profile.get("user_id")) != str(user_id):
            raise UnauthorizedError()
        self._delete_resume_file(resume_id)
        self._candidates.update_resume(str(doc["candidate_id"]), None)
        return True

    def _delete_resume_file(self, resume_id) -> None:
        doc = self._resumes.find_by_id(resume_id)
        if doc:
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            file_path = os.path.join(upload_folder, doc.get("stored_filename", ""))
            if os.path.exists(file_path):
                os.remove(file_path)
            self._resumes.delete_by_id(resume_id)

    def get_by_candidate(self, candidate_profile_id: str):
        doc = self._resumes.find_by_candidate(candidate_profile_id)
        return serialize_doc(doc) if doc else None
