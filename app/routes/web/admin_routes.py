"""
Web routes for the admin portal.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService
from app.services.notification_service import NotificationService
from app.services.company_service import CompanyService
from app.services.candidate_service import CandidateService
from app.services.recruiter_service import RecruiterService
from app.repositories.user_repository import UserRepository
from app.middleware.audit_middleware import AuditLogger
from app.utils.decorators import admin_required
from app.utils.helpers import serialize_doc

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

_analytics = AnalyticsService()
_report_svc = ReportService()
_notif_svc = NotificationService()
_company_svc = CompanyService()
_cand_svc = CandidateService()
_rec_svc = RecruiterService()
_users = UserRepository()


@admin_bp.route("/users")
@admin_required
def users():
    page = int(request.args.get("page", 1))
    role_filter = request.args.get("role", "")
    filters = {"role": role_filter} if role_filter else {}
    result = _users.find_all(filters=filters, page=page, per_page=20)
    result["items"] = [serialize_doc(u) for u in result["items"]]
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template("admin/users.html", result=result, role_filter=role_filter, unread=unread)


@admin_bp.route("/users/<user_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_user_active(user_id):
    user_doc = _users.find_by_id(user_id)
    if user_doc:
        new_status = not user_doc.get("is_active", True)
        _users.set_active(user_id, new_status)
        action = "activated" if new_status else "deactivated"
        if not new_status:
            AuditLogger.log(session["user_id"], AuditLogger.USER_DEACTIVATED, "users", user_id)
        flash(f"User {action}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/companies")
@admin_required
def companies():
    page = int(request.args.get("page", 1))
    result = _company_svc.list_all(page=page)
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template("admin/companies.html", result=result, unread=unread)


@admin_bp.route("/companies/<company_id>/verify", methods=["POST"])
@admin_required
def verify_company(company_id):
    try:
        _company_svc.verify_company(company_id)
        flash("Company verified.", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.companies"))


@admin_bp.route("/analytics")
@admin_required
def analytics():
    overview = _analytics.get_admin_overview()
    jobs_by_skill = _analytics.get_jobs_by_skill()
    jobs_by_location = _analytics.get_jobs_by_location()
    apps_by_status = _analytics.get_applications_by_status()
    monthly_apps = _analytics.get_monthly_applications()
    monthly_regs = _analytics.get_monthly_registrations()
    apps_by_company = _analytics.get_applications_by_company()
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template(
        "admin/analytics.html",
        overview=overview,
        jobs_by_skill=jobs_by_skill,
        jobs_by_location=jobs_by_location,
        apps_by_status=apps_by_status,
        monthly_apps=monthly_apps,
        monthly_regs=monthly_regs,
        apps_by_company=apps_by_company,
        unread=unread,
    )


@admin_bp.route("/reports")
@admin_required
def reports():
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template("admin/reports.html", unread=unread)


@admin_bp.route("/reports/candidates")
@admin_required
def report_candidates():
    filters = {
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "location": request.args.get("location", ""),
    }
    if request.args.get("download"):
        csv_data = _report_svc.candidate_csv(filters)
        return Response(csv_data, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=candidates.csv"})
    data = _report_svc.candidate_report(filters)
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template("admin/report_candidates.html", data=data, filters=filters, unread=unread)


@admin_bp.route("/reports/jobs")
@admin_required
def report_jobs():
    filters = {
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "status": request.args.get("status", ""),
        "location": request.args.get("location", ""),
    }
    if request.args.get("download"):
        csv_data = _report_svc.job_csv(filters)
        return Response(csv_data, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=jobs.csv"})
    data = _report_svc.job_report(filters)
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template("admin/report_jobs.html", data=data, filters=filters, unread=unread)


@admin_bp.route("/reports/applications")
@admin_required
def report_applications():
    filters = {
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "status": request.args.get("status", ""),
    }
    if request.args.get("download"):
        csv_data = _report_svc.application_csv(filters)
        return Response(csv_data, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=applications.csv"})
    data = _report_svc.application_report(filters)
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template("admin/report_applications.html", data=data, filters=filters, unread=unread)


@admin_bp.route("/audit-logs")
@admin_required
def audit_logs():
    page = int(request.args.get("page", 1))
    action_filter = request.args.get("action", "")
    filters = {"action": action_filter} if action_filter else {}
    result = AuditLogger.get_logs(page=page, per_page=50, filters=filters)
    result["items"] = [serialize_doc(l) for l in result["items"]]
    unread = _notif_svc.count_unread(session["user_id"])
    return render_template("admin/audit_logs.html", result=result, action_filter=action_filter, unread=unread)
