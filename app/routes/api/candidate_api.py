"""
REST API — candidate endpoints.
"""
from flask import Blueprint, request, jsonify, session
from app.services.candidate_service import CandidateService
from app.utils.decorators import login_required, candidate_required
from app.exceptions.app_exceptions import UserNotFoundError, UnauthorizedError

candidate_api_bp = Blueprint("candidate_api", __name__)
_svc = CandidateService()


@candidate_api_bp.route("/<candidate_id>", methods=["GET"])
@login_required
def get_candidate(candidate_id):
    try:
        profile = _svc.get_profile(candidate_id)
        # Only candidate owner or recruiter/admin can view
        if session.get("role") == "CANDIDATE" and session.get("profile_id") != candidate_id:
            return jsonify({"success": False, "message": "Unauthorized.", "error_code": "UNAUTHORIZED"}), 403
        return jsonify({"success": True, "message": "OK", "data": profile}), 200
    except UserNotFoundError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), 404


@candidate_api_bp.route("/<candidate_id>", methods=["PUT"])
@candidate_required
def update_candidate(candidate_id):
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = session["user_id"]
    try:
        profile = _svc.update_profile(candidate_id, user_id, data)
        return jsonify({"success": True, "message": "Profile updated.", "data": profile}), 200
    except (UserNotFoundError, UnauthorizedError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
