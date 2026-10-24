"""
General-purpose utility helpers.
"""
import re
import uuid
import os
from datetime import datetime
from bson import ObjectId
from typing import Any, Optional


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number (10–15 digits, optional leading +)."""
    pattern = r"^\+?[0-9]{10,15}$"
    return bool(re.match(pattern, phone.strip()))


def is_valid_object_id(oid: str) -> bool:
    """Check whether a string is a valid MongoDB ObjectId."""
    try:
        ObjectId(oid)
        return True
    except Exception:
        return False


def to_object_id(oid: Any) -> Optional[ObjectId]:
    """Safely convert a string to ObjectId; return None on failure."""
    try:
        return ObjectId(str(oid))
    except Exception:
        return None


def serialize_doc(doc: dict) -> dict:
    """
    Recursively convert MongoDB document to JSON-serialisable dict.
    Converts ObjectId → str, datetime → ISO-8601 string.
    """
    if doc is None:
        return {}
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(v) if isinstance(v, dict) else (str(v) if isinstance(v, ObjectId) else v) for v in value]
        else:
            result[key] = value
    return result


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename preserving the original extension."""
    ext = os.path.splitext(original_filename)[1].lower()
    unique = uuid.uuid4().hex
    return f"{unique}{ext}"


def paginate(query_cursor, page: int, per_page: int) -> dict:
    """
    Return a pagination dict with items and metadata.
    Works with a list of already-fetched documents.
    """
    total = len(query_cursor)
    start = (page - 1) * per_page
    end = start + per_page
    items = query_cursor[start:end]
    total_pages = (total + per_page - 1) // per_page
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }


def success_response(message: str = "Success", data: Any = None, status_code: int = 200):
    """Build a standard success JSON response dict."""
    return {"success": True, "message": message, "data": data or {}}, status_code


def error_response(message: str = "Error", error_code: str = "ERROR", status_code: int = 400):
    """Build a standard error JSON response dict."""
    return {"success": False, "message": message, "error_code": error_code}, status_code


def calculate_profile_completion(profile: dict) -> int:
    """Calculate profile completion percentage for a candidate."""
    fields = ["name", "email", "phone", "location", "skills", "education", "experience", "expected_salary", "notice_period"]
    filled = sum(1 for f in fields if profile.get(f))
    has_resume = bool(profile.get("resume_id"))
    total = len(fields) + 1  # +1 for resume
    return int(((filled + (1 if has_resume else 0)) / total) * 100)
