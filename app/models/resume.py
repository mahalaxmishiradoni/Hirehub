"""
Resume domain model.
"""
from datetime import datetime
from typing import Optional


class Resume:
    """
    Represents an uploaded resume file with metadata.
    """

    ALLOWED_EXTENSIONS: set = {"pdf", "doc", "docx"}

    def __init__(
        self,
        candidate_id,
        original_filename: str,
        stored_filename: str,
        file_size: int,
        uploaded_at: Optional[datetime] = None,
        _id=None,
    ) -> None:
        self._id = _id
        self.candidate_id = candidate_id
        self.original_filename = original_filename
        self.stored_filename = stored_filename
        self.file_size = file_size
        self.uploaded_at = uploaded_at or datetime.utcnow()

    @property
    def id(self) -> Optional[str]:
        return str(self._id) if self._id else None

    @property
    def extension(self) -> str:
        """Return the file extension."""
        return self.stored_filename.rsplit(".", 1)[-1].lower() if "." in self.stored_filename else ""

    @staticmethod
    def is_allowed_extension(filename: str) -> bool:
        """Check if the filename has an allowed extension."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return ext in Resume.ALLOWED_EXTENSIONS

    @classmethod
    def from_dict(cls, data: dict) -> "Resume":
        return cls(
            _id=data.get("_id"),
            candidate_id=data.get("candidate_id"),
            original_filename=data.get("original_filename", ""),
            stored_filename=data.get("stored_filename", ""),
            file_size=data.get("file_size", 0),
            uploaded_at=data.get("uploaded_at"),
        )

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at,
        }

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file={self.original_filename}>"
