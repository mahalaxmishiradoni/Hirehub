"""
Web routes for the recruiter portal.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file
from app.services.recruiter_service import RecruiterService
from app.services.company_service import CompanyService
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.interview_service import InterviewService
from app.services.notification_service import NotificationService
from app.services.resume_service import ResumeService
from app.services.analytics_service import AnalyticsService
from app.utils.decorators import recruiter_required
from app.exceptions.app_exceptions import ValidationError, UnauthorizedError, JobNotFoundError

recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/recruiter")

_rec_svc = RecruiterService()
_company_svc = CompanyService()
_job_svc = JobService()
_app_svc = ApplicationService()
_interview_svc = InterviewService()
_notif_svc = NotificationService()
_resume_svc = ResumeService()
_analytics = AnalyticsService()


@recruiter_bp.route("/profile")
@recruiter_required
def profile():
    user_id = session["user_id"]
    recruiter = _rec_svc.get_profile_by_user_id(user_id)
    company_id = session.get("company_id", "")
    company = _company_svc.get_company(company_id) if company_id else {}
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/profile.html", recruiter=recruiter, company=company, unread=unread)


@recruiter_bp.route("/profile/edit", methods=["GET", "POST"])
@recruiter_required
def edit_profile():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    if request.method == "POST":
        try:
            _rec_svc.update_profile(profile_id, user_id, request.form.to_dict())
            flash("Profile updated.", "success")
            return redirect(url_for("recruiter.profile"))
        except Exception as e:
            flash(str(e), "danger")
    recruiter = _rec_svc.get_profile_by_user_id(user_id)
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/edit_profile.html", recruiter=recruiter, unread=unread)


@recruiter_bp.route("/company/edit", methods=["GET", "POST"])
@recruiter_required
def edit_company():
    user_id = session["user_id"]
    company_id = session.get("company_id", "")
    if request.method == "POST":
        try:
            _company_svc.update_company(company_id, user_id, request.form.to_dict())
            flash("Company updated.", "success")
            return redirect(url_for("recruiter.profile"))
        except Exception as e:
            flash(str(e), "danger")
    company = _company_svc.get_company(company_id) if company_id else {}
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/edit_company.html", company=company, unread=unread)


@recruiter_bp.route("/jobs")
@recruiter_required
def my_jobs():
    user_id = session["user_id"]
    page = int(request.args.get("page", 1))
    result = _job_svc.get_recruiter_jobs(user_id, page=page)
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/my_jobs.html", result=result, unread=unread)


@recruiter_bp.route("/jobs/create", methods=["GET", "POST"])
@recruiter_required
def create_job():
    user_id = session["user_id"]
    company_id = session.get("company_id", "")
    if request.method == "POST":
        try:
            _job_svc.create_job(request.form.to_dict(), user_id, company_id)
            flash("Job posted successfully.", "success")
            return redirect(url_for("recruiter.my_jobs"))
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception as e:
            flash("Failed to create job.", "danger")
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/create_job.html", unread=unread)


@recruiter_bp.route("/jobs/<job_id>/edit", methods=["GET", "POST"])
@recruiter_required
def edit_job(job_id):
    user_id = session["user_id"]
    try:
        job = _job_svc.get_job(job_id)
    except JobNotFoundError:
        flash("Job not found.", "danger")
        return redirect(url_for("recruiter.my_jobs"))
    if request.method == "POST":
        try:
            _job_svc.update_job(job_id, user_id, request.form.to_dict())
            flash("Job updated.", "success")
            return redirect(url_for("recruiter.my_jobs"))
        except (ValidationError, UnauthorizedError) as e:
            flash(e.message, "danger")
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/edit_job.html", job=job, unread=unread)


@recruiter_bp.route("/jobs/<job_id>/close", methods=["POST"])
@recruiter_required
def close_job(job_id):
    user_id = session["user_id"]
    try:
        _job_svc.close_job(job_id, user_id)
        flash("Job closed.", "info")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("recruiter.my_jobs"))


@recruiter_bp.route("/jobs/<job_id>/applicants")
@recruiter_required
def applicants(job_id):
    user_id = session["user_id"]
    page = int(request.args.get("page", 1))
    try:
        job = _job_svc.get_job(job_id)
        result = _app_svc.get_job_applications(job_id, user_id, page=page)
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("recruiter.my_jobs"))
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/applicants.html", job=job, result=result, unread=unread)


@recruiter_bp.route("/applications/<app_id>/update", methods=["POST"])
@recruiter_required
def update_application(app_id):
    user_id = session["user_id"]
    new_status = request.form.get("status", "")
    notes = request.form.get("recruiter_notes", "")
    job_id = request.form.get("job_id", "")
    try:
        _app_svc.update_status(app_id, new_status, user_id, notes)
        flash(f"Application status updated to {new_status}.", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("recruiter.applicants", job_id=job_id) if job_id else url_for("recruiter.my_jobs"))


@recruiter_bp.route("/applications/<app_id>/schedule-interview", methods=["GET", "POST"])
@recruiter_required
def schedule_interview(app_id):
    user_id = session["user_id"]
    if request.method == "POST":
        try:
            _interview_svc.schedule_interview(app_id, user_id, request.form.to_dict())
            flash("Interview scheduled successfully.", "success")
            return redirect(url_for("recruiter.my_jobs"))
        except Exception as e:
            flash(str(e), "danger")
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/schedule_interview.html", app_id=app_id, unread=unread)


@recruiter_bp.route("/interviews")
@recruiter_required
def interviews():
    user_id = session["user_id"]
    page = int(request.args.get("page", 1))
    result = _interview_svc.get_recruiter_interviews(user_id, page=page)
    unread = _notif_svc.count_unread(user_id)
    return render_template("recruiter/interviews.html", result=result, unread=unread)


@recruiter_bp.route("/resume/<resume_id>/download")
@recruiter_required
def download_resume(resume_id):
    user_id = session["user_id"]
    role = session.get("role", "RECRUITER")
    try:
        file_path = _resume_svc.get_file_path(resume_id, user_id, role)
        doc = _resume_svc.get_resume(resume_id, user_id, role)
        return send_file(file_path, as_attachment=True, download_name=doc.get("original_filename", "resume"))
    except Exception:
        flash("Resume not available.", "danger")
        return redirect(url_for("recruiter.my_jobs"))


@recruiter_bp.route("/analytics")
@recruiter_required
def analytics():
    user_id = session["user_id"]
    stats = _analytics.get_recruiter_stats(user_id)
    apps_by_status = _analytics.get_applications_by_status()
    unread = _notif_svc.count_unread(user_id)
    return render_template(
        "recruiter/analytics.html",
        stats=stats,
        apps_by_status=apps_by_status,
        unread=unread,
    )
