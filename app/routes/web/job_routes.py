"""
Web routes for job browsing, details, and search.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.matching_service import MatchingService
from app.services.notification_service import NotificationService
from app.repositories.candidate_repository import CandidateRepository
from app.utils.decorators import login_required, candidate_required
from app.exceptions.app_exceptions import JobNotFoundError, JobClosedError, DuplicateApplicationError

job_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

_job_service = JobService()
_app_service = ApplicationService()
_notif = NotificationService()
_candidates = CandidateRepository()


@job_bp.route("/")
def list_jobs():
    page = int(request.args.get("page", 1))
    filters = {
        "keyword": request.args.get("keyword", ""),
        "skills": request.args.get("skills", ""),
        "location": request.args.get("location", ""),
        "salary_min": request.args.get("salary_min", ""),
        "salary_max": request.args.get("salary_max", ""),
        "experience_min": request.args.get("experience_min", ""),
        "experience_max": request.args.get("experience_max", ""),
        "work_mode": request.args.get("work_mode", ""),
        "employment_type": request.args.get("employment_type", ""),
    }
    result = _job_service.search_jobs(filters, page=page, per_page=10)
    unread = _notif.count_unread(session.get("user_id")) if "user_id" in session else 0
    return render_template("jobs/list.html", result=result, filters=filters, page=page, unread=unread)


@job_bp.route("/<job_id>")
def job_detail(job_id):
    try:
        job = _job_service.get_job(job_id)
    except JobNotFoundError:
        return render_template("errors/404.html"), 404

    match_result = None
    user_application = None
    if session.get("role") == "CANDIDATE":
        profile_id = session.get("profile_id")
        if profile_id:
            profile = _candidates.find_by_id(profile_id)
            if profile:
                from app.utils.helpers import serialize_doc
                match_result = MatchingService.calculate_match(serialize_doc(profile), job)
            # Check if already applied
            from app.utils.helpers import to_object_id
            existing = _app_service._apps.find_by_candidate_and_job(
                to_object_id(profile_id), to_object_id(job_id)
            )
            if existing:
                from app.utils.helpers import serialize_doc as sd
                user_application = sd(existing)

    unread = _notif.count_unread(session.get("user_id")) if "user_id" in session else 0
    return render_template(
        "jobs/detail.html",
        job=job,
        match_result=match_result,
        user_application=user_application,
        unread=unread,
    )


@job_bp.route("/<job_id>/apply", methods=["POST"])
@candidate_required
def apply_job(job_id):
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    try:
        _app_service.apply(profile_id, user_id, job_id)
        flash("Application submitted successfully!", "success")
    except (JobNotFoundError, JobClosedError, DuplicateApplicationError) as e:
        flash(e.message, "danger")
    except Exception:
        flash("Failed to apply. Please try again.", "danger")
    return redirect(url_for("jobs.job_detail", job_id=job_id))


@job_bp.route("/<job_id>/save", methods=["POST"])
@candidate_required
def save_job(job_id):
    from app.services.candidate_service import CandidateService
    svc = CandidateService()
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    try:
        svc.save_job(profile_id, user_id, job_id)
        flash("Job saved!", "success")
    except Exception:
        flash("Could not save job.", "danger")
    return redirect(url_for("jobs.job_detail", job_id=job_id))


@job_bp.route("/<job_id>/unsave", methods=["POST"])
@candidate_required
def unsave_job(job_id):
    from app.services.candidate_service import CandidateService
    svc = CandidateService()
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    try:
        svc.unsave_job(profile_id, user_id, job_id)
        flash("Job removed from saved.", "info")
    except Exception:
        flash("Could not unsave job.", "danger")
    return redirect(url_for("jobs.job_detail", job_id=job_id))
