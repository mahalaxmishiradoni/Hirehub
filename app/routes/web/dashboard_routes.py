"""
Dashboard routes — role-specific home pages after login.
"""
from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.decorators import login_required
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from app.services.recommendation_service import RecommendationService
from app.services.application_service import ApplicationService
from app.services.job_service import JobService
from app.repositories.user_repository import UserRepository

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

_analytics = AnalyticsService()
_notif = NotificationService()
_recs = RecommendationService()
_apps = ApplicationService()
_jobs = JobService()
_users = UserRepository()


@dashboard_bp.route("/")
@login_required
def home():
    role = session.get("role")
    if role == "CANDIDATE":
        return redirect(url_for("dashboard.candidate"))
    elif role == "RECRUITER":
        return redirect(url_for("dashboard.recruiter"))
    elif role == "ADMIN":
        return redirect(url_for("dashboard.admin"))
    return redirect(url_for("auth.login"))


@dashboard_bp.route("/candidate")
@login_required
def candidate():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    unread = _notif.count_unread(user_id)
    stats = _analytics.get_candidate_stats(profile_id) if profile_id else {}
    recommendations = []
    if profile_id:
        try:
            recommendations = _recs.get_recommendations(profile_id, limit=5)
        except Exception:
            pass
    recent_apps = []
    if profile_id:
        try:
            result = _apps.get_candidate_applications(profile_id, user_id, page=1, per_page=5)
            recent_apps = result.get("items", [])
        except Exception:
            pass
    return render_template(
        "dashboard/candidate_dashboard.html",
        stats=stats,
        recommendations=recommendations,
        recent_apps=recent_apps,
        unread=unread,
    )


@dashboard_bp.route("/recruiter")
@login_required
def recruiter():
    user_id = session["user_id"]
    unread = _notif.count_unread(user_id)
    stats = _analytics.get_recruiter_stats(user_id)
    recent_jobs = _jobs.get_recruiter_jobs(user_id, page=1, per_page=5).get("items", [])
    return render_template(
        "dashboard/recruiter_dashboard.html",
        stats=stats,
        recent_jobs=recent_jobs,
        unread=unread,
    )


@dashboard_bp.route("/admin")
@login_required
def admin():
    user_id = session["user_id"]
    if session.get("role") != "ADMIN":
        return redirect(url_for("dashboard.home"))
    unread = _notif.count_unread(user_id)
    overview = _analytics.get_admin_overview()
    return render_template(
        "dashboard/admin_dashboard.html",
        overview=overview,
        unread=unread,
    )
