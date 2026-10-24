"""
REST API — application endpoints.
"""
from flask import Blueprint, request, jsonify, session
from app.services.application_service import ApplicationService
from app.utils.decorators import login_required, recruiter_required
from app.exceptions.app_exceptions import (
    ApplicationNotFoundError, UnauthorizedError,
    DuplicateApplicationError, JobClosedError, JobNotFoundError
)

application_api_bp = Blueprint("application_api", __name__)
_svc = ApplicationService()


@application_api_bp.route("", methods=["GET"])
@login_required
def list_applications():
    user_id = session["user_id"]
    role = session.get("role")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    if role == "CANDIDATE":
        profile_id = session.get("profile_id", "")
        result = _svc.get_candidate_applications(profile_id, user_id, page, per_page)
    elif role in ("RECRUITER", "ADMIN"):
        result = _svc.get_all_applications(page, per_page)
    else:
        return jsonify({"success": False, "message": "Forbidden.", "error_code": "UNAUTHORIZED"}), 403
    return jsonify({"success": True, "message": "OK", "data": result}), 200


@application_api_bp.route("/<app_id>", methods=["GET"])
@login_required
def get_application(app_id):
    user_id = session["user_id"]
    role = session.get("role", "")
    try:
        app = _svc.get_application(app_id, user_id, role)
        return jsonify({"success": True, "message": "OK", "data": app}), 200
    except (ApplicationNotFoundError, UnauthorizedError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code


@application_api_bp.route("/<app_id>/status", methods=["PUT"])
@recruiter_required
def update_status(app_id):
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = session["user_id"]
    new_status = data.get("status", "")
    notes = data.get("recruiter_notes", "")
    try:
        result = _svc.update_status(app_id, new_status, user_id, notes)
        return jsonify({"success": True, "message": f"Status updated to {new_status}.", "data": result}), 200
    except (ApplicationNotFoundError, UnauthorizedError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "ERROR"}), 400
