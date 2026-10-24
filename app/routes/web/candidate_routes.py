"""
Web routes for the candidate portal.
"""
import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file
from app.services.candidate_service import CandidateService
from app.services.application_service import ApplicationService
from app.services.interview_service import InterviewService
from app.services.resume_service import ResumeService
from app.services.notification_service import NotificationService
from app.services.recommendation_service import RecommendationService
from app.utils.decorators import candidate_required
from app.exceptions.app_exceptions import UnauthorizedError, ValidationError

candidate_bp = Blueprint("candidate", __name__, url_prefix="/candidate")

_cand_svc = CandidateService()
_app_svc = ApplicationService()
_interview_svc = InterviewService()
_resume_svc = ResumeService()
_notif_svc = NotificationService()
_rec_svc = RecommendationService()


@candidate_bp.route("/profile")
@candidate_required
def profile():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    data = _cand_svc.get_profile(profile_id)
    resume = _resume_svc.get_by_candidate(profile_id)
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/profile.html", profile=data, resume=resume, unread=unread)


@candidate_bp.route("/profile/edit", methods=["GET", "POST"])
@candidate_required
def edit_profile():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    if request.method == "POST":
        import json as _json
        data = request.form.to_dict()
        # Skills as list
        skills_raw = request.form.get("skills", "")
        data["skills"] = [s.strip() for s in skills_raw.split(",") if s.strip()]
        # Parse JSON experience / education fields from _raw textarea names
        for field in ("experience", "education"):
            raw_val = data.pop(f"{field}_raw", None)
            if raw_val is not None:
                try:
                    data[field] = _json.loads(raw_val) if raw_val.strip() else []
                except (ValueError, TypeError):
                    data[field] = []
        try:
            _cand_svc.update_profile(profile_id, user_id, data)
            flash("Profile updated successfully.", "success")
            return redirect(url_for("candidate.profile"))
        except (ValidationError, UnauthorizedError) as e:
            flash(e.message, "danger")
        except Exception:
            flash("Update failed.", "danger")
    profile_data = _cand_svc.get_profile(profile_id)
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/edit_profile.html", profile=profile_data, unread=unread)


@candidate_bp.route("/resume/upload", methods=["GET", "POST"])
@candidate_required
def upload_resume():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    if request.method == "POST":
        file = request.files.get("resume")
        try:
            _resume_svc.upload_resume(file, profile_id, user_id)
            flash("Resume uploaded successfully.", "success")
            return redirect(url_for("candidate.profile"))
        except Exception as e:
            flash(str(e), "danger")
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/upload_resume.html", unread=unread)


@candidate_bp.route("/resume/download/<resume_id>")
@candidate_required
def download_resume(resume_id):
    user_id = session["user_id"]
    role = session.get("role", "CANDIDATE")
    try:
        file_path = _resume_svc.get_file_path(resume_id, user_id, role)
        doc = _resume_svc.get_resume(resume_id, user_id, role)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=doc.get("original_filename", "resume"),
        )
    except Exception as e:
        flash("Resume not available.", "danger")
        return redirect(url_for("candidate.profile"))


@candidate_bp.route("/applications")
@candidate_required
def applications():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    page = int(request.args.get("page", 1))
    result = _app_svc.get_candidate_applications(profile_id, user_id, page=page)
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/applications.html", result=result, unread=unread)


@candidate_bp.route("/applications/<app_id>/withdraw", methods=["POST"])
@candidate_required
def withdraw_application(app_id):
    user_id = session["user_id"]
    try:
        _app_svc.withdraw(app_id, user_id)
        flash("Application withdrawn.", "info")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("candidate.applications"))


@candidate_bp.route("/interviews")
@candidate_required
def interviews():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    page = int(request.args.get("page", 1))
    result = _interview_svc.get_candidate_interviews(profile_id, user_id, page=page)
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/interviews.html", result=result, unread=unread)


@candidate_bp.route("/notifications")
@candidate_required
def notifications():
    user_id = session["user_id"]
    page = int(request.args.get("page", 1))
    result = _notif_svc.get_for_user(user_id, page=page)
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/notifications.html", result=result, unread=unread)


@candidate_bp.route("/notifications/<notif_id>/read", methods=["POST"])
@candidate_required
def mark_notification_read(notif_id):
    user_id = session["user_id"]
    _notif_svc.mark_read(notif_id, user_id)
    return redirect(url_for("candidate.notifications"))


@candidate_bp.route("/saved-jobs")
@candidate_required
def saved_jobs():
    from app.services.job_service import JobService
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    job_ids = _cand_svc.get_saved_jobs(profile_id)
    job_svc = JobService()
    jobs = []
    for jid in job_ids:
        try:
            jobs.append(job_svc.get_job(jid))
        except Exception:
            pass
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/saved_jobs.html", jobs=jobs, unread=unread)


@candidate_bp.route("/recommendations")
@candidate_required
def recommendations():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    recs = []
    try:
        recs = _rec_svc.get_recommendations(profile_id, limit=10)
    except Exception:
        pass
    unread = _notif_svc.count_unread(user_id)
    return render_template("candidate/recommendations.html", recommendations=recs, unread=unread)
