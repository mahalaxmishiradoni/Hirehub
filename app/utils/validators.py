"""
Server-side input validators.
"""
from datetime import date, datetime
from typing import Optional
from app.utils.helpers import is_valid_email, is_valid_phone, is_valid_object_id
from app.exceptions.app_exceptions import ValidationError


def validate_registration(data: dict, role: str = "CANDIDATE") -> None:
    """Validate common registration fields."""
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    confirm = data.get("confirm_password") or ""

    if not name or len(name) < 2:
        raise ValidationError("Name must be at least 2 characters.", "name")
    if not email or not is_valid_email(email):
        raise ValidationError("A valid email address is required.", "email")
    if not phone or not is_valid_phone(phone):
        raise ValidationError("A valid phone number (10–15 digits) is required.", "phone")
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters.", "password")
    if password != confirm:
        raise ValidationError("Passwords do not match.", "confirm_password")
    if role == "RECRUITER":
        company_name = (data.get("company_name") or "").strip()
        if not company_name:
            raise ValidationError("Company name is required for recruiters.", "company_name")


def validate_job(data: dict) -> None:
    """Validate job creation/update fields."""
    if not (data.get("title") or "").strip():
        raise ValidationError("Job title is required.", "title")
    if not (data.get("description") or "").strip():
        raise ValidationError("Job description is required.", "description")
    if not (data.get("location") or "").strip():
        raise ValidationError("Location is required.", "location")

    work_modes = {"REMOTE", "HYBRID", "ONSITE"}
    if data.get("work_mode") not in work_modes:
        raise ValidationError(f"Work mode must be one of {work_modes}.", "work_mode")

    employment_types = {"FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT"}
    if data.get("employment_type") not in employment_types:
        raise ValidationError(f"Employment type must be one of {employment_types}.", "employment_type")

    try:
        exp_min = int(data.get("experience_min", 0))
        exp_max = int(data.get("experience_max", 0))
        if exp_min < 0 or exp_max < 0:
            raise ValidationError("Experience values must be non-negative.", "experience_min")
        if exp_max < exp_min:
            raise ValidationError("Max experience must be >= min experience.", "experience_max")
    except (ValueError, TypeError):
        raise ValidationError("Experience must be numeric.", "experience_min")

    try:
        sal_min = float(data.get("salary_min", 0))
        sal_max = float(data.get("salary_max", 0))
        if sal_min < 0 or sal_max < 0:
            raise ValidationError("Salary values must be non-negative.", "salary_min")
    except (ValueError, TypeError):
        raise ValidationError("Salary must be numeric.", "salary_min")


def validate_file_upload(filename: str, file_size: int, max_size: int, allowed_extensions: set) -> None:
    """Validate uploaded file extension and size."""
    if not filename:
        raise ValidationError("No file provided.", "file")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed_extensions:
        raise ValidationError(f"File type not allowed. Allowed: {', '.join(allowed_extensions)}.", "file")
    if file_size > max_size:
        raise ValidationError(f"File size exceeds limit of {max_size // (1024 * 1024)} MB.", "file")


def validate_object_id(oid: str, field: str = "id") -> None:
    """Raise ValidationError if oid is not a valid ObjectId."""
    if not is_valid_object_id(oid):
        raise ValidationError(f"Invalid {field} format.", field)


def validate_date_string(date_str: str, field: str = "date") -> date:
    """Parse and return a date from ISO string, raise ValidationError on failure."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid date format for {field}. Use YYYY-MM-DD.", field)
