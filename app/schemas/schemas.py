"""
Schema definitions (allowed fields, defaults) used by services for data normalisation.
Not an ORM — just plain dicts that document shape.
"""
from datetime import datetime


def user_schema(name: str, email: str, phone: str, password_hash: str, role: str) -> dict:
    return {
        "name": name,
        "email": email.lower().strip(),
        "phone": phone.strip(),
        "password_hash": password_hash,
        "role": role,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def candidate_schema(user_id, name: str, email: str, phone: str = "") -> dict:
    return {
        "user_id": user_id,
        "name": name,
        "email": email.lower().strip(),
        "phone": phone.strip(),
        "location": "",
        "skills": [],
        "education": [],
        "experience": [],
        "expected_salary": None,
        "notice_period": None,
        "resume_id": None,
        "saved_jobs": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def recruiter_schema(user_id, name: str, email: str, company_id) -> dict:
    return {
        "user_id": user_id,
        "name": name,
        "email": email.lower().strip(),
        "phone": "",
        "company_id": company_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def company_schema(name: str, recruiter_id) -> dict:
    return {
        "name": name,
        "description": "",
        "website": "",
        "location": "",
        "industry": "",
        "size": "",
        "logo_url": "",
        "is_verified": False,
        "recruiter_id": recruiter_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def job_schema(data: dict, recruiter_id, company_id) -> dict:
    return {
        "company_id": company_id,
        "recruiter_id": recruiter_id,
        "title": data.get("title", "").strip(),
        "description": data.get("description", "").strip(),
        "skills": [s.strip() for s in data.get("skills", []) if s.strip()],
        "experience_min": int(data.get("experience_min", 0)),
        "experience_max": int(data.get("experience_max", 0)),
        "location": data.get("location", "").strip(),
        "work_mode": data.get("work_mode", "ONSITE"),
        "employment_type": data.get("employment_type", "FULL_TIME"),
        "salary_min": float(data.get("salary_min", 0)),
        "salary_max": float(data.get("salary_max", 0)),
        "posted_date": datetime.utcnow(),
        "deadline": data.get("deadline"),
        "status": "OPEN",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def application_schema(candidate_id, job_id) -> dict:
    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "status": "APPLIED",
        "applied_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "recruiter_notes": "",
        "interview_id": None,
    }


def interview_schema(data: dict, application_id, candidate_id, recruiter_id) -> dict:
    return {
        "application_id": application_id,
        "candidate_id": candidate_id,
        "recruiter_id": recruiter_id,
        "date": data.get("date"),
        "time": data.get("time"),
        "type": data.get("type", "ONLINE"),
        "meeting_link": data.get("meeting_link", ""),
        "status": "SCHEDULED",
        "feedback": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def resume_schema(candidate_id, original_filename: str, stored_filename: str, file_size: int) -> dict:
    return {
        "candidate_id": candidate_id,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_size": file_size,
        "uploaded_at": datetime.utcnow(),
    }


def notification_schema(user_id, title: str, message: str, notif_type: str, resource_id=None) -> dict:
    return {
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": notif_type,
        "resource_id": resource_id,
        "is_read": False,
        "created_at": datetime.utcnow(),
    }


def audit_log_schema(user_id, action: str, resource: str, resource_id=None, metadata: dict = None) -> dict:
    return {
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow(),
    }
