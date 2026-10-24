"""
REST API — recruiter endpoints.
"""
from flask import Blueprint, request, jsonify, session
from app.services.recruiter_service import RecruiterService
from app.utils.decorators import login_required, recruiter_required
from app.exceptions.app_exceptions import UserNotFoundError, UnauthorizedError

recruiter_api_bp = Blueprint("recruiter_api", __name__)
_svc = RecruiterService()


@recruiter_api_bp.route("/<recruiter_id>", methods=["GET"])
@login_required
def get_recruiter(recruiter_id):
    try:
        profile = _svc.get_profile(recruiter_id)
        return jsonify({"success": True, "message": "OK", "data": profile}), 200
    except UserNotFoundError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), 404


@recruiter_api_bp.route("/<recruiter_id>", methods=["PUT"])
@recruiter_required
def update_recruiter(recruiter_id):
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = session["user_id"]
    try:
        profile = _svc.update_profile(recruiter_id, user_id, data)
        return jsonify({"success": True, "message": "Profile updated.", "data": profile}), 200
    except (UserNotFoundError, UnauthorizedError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
