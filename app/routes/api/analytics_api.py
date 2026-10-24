"""
REST API — analytics endpoints.
"""
from flask import Blueprint, jsonify, session
from app.services.analytics_service import AnalyticsService
from app.utils.decorators import login_required, admin_required

analytics_api_bp = Blueprint("analytics_api", __name__)
_svc = AnalyticsService()


@analytics_api_bp.route("/candidate", methods=["GET"])
@login_required
def candidate_analytics():
    profile_id = session.get("profile_id", "")
    data = _svc.get_candidate_stats(profile_id)
    return jsonify({"success": True, "message": "OK", "data": data}), 200


@analytics_api_bp.route("/recruiter", methods=["GET"])
@login_required
def recruiter_analytics():
    user_id = session.get("user_id", "")
    data = _svc.get_recruiter_stats(user_id)
    return jsonify({"success": True, "message": "OK", "data": data}), 200


@analytics_api_bp.route("/admin", methods=["GET"])
@admin_required
def admin_analytics():
    data = {
        "overview": _svc.get_admin_overview(),
        "jobs_by_skill": _svc.get_jobs_by_skill(),
        "jobs_by_location": _svc.get_jobs_by_location(),
        "apps_by_status": _svc.get_applications_by_status(),
        "monthly_apps": _svc.get_monthly_applications(),
        "monthly_regs": _svc.get_monthly_registrations(),
    }
    return jsonify({"success": True, "message": "OK", "data": data}), 200
