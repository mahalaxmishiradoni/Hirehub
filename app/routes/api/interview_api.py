"""
REST API — interview endpoints.
"""
from flask import Blueprint, request, jsonify, session
from app.services.interview_service import InterviewService
from app.utils.decorators import login_required, recruiter_required
from app.exceptions.app_exceptions import InterviewNotFoundError, UnauthorizedError

interview_api_bp = Blueprint("interview_api", __name__)
_svc = InterviewService()


@interview_api_bp.route("", methods=["POST"])
@recruiter_required
def schedule_interview():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = session["user_id"]
    application_id = data.get("application_id", "")
    try:
        result = _svc.schedule_interview(application_id, user_id, data)
        return jsonify({"success": True, "message": "Interview scheduled.", "data": result}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "ERROR"}), 400


@interview_api_bp.route("", methods=["GET"])
@login_required
def list_interviews():
    user_id = session["user_id"]
    role = session.get("role")
    page = int(request.args.get("page", 1))
    if role == "CANDIDATE":
        profile_id = session.get("profile_id", "")
        result = _svc.get_candidate_interviews(profile_id, user_id, page)
    elif role == "RECRUITER":
        result = _svc.get_recruiter_interviews(user_id, page)
    else:
        result = {"items": [], "page": 1, "total": 0}
    return jsonify({"success": True, "message": "OK", "data": result}), 200


@interview_api_bp.route("/<interview_id>", methods=["PUT"])
@recruiter_required
def update_interview(interview_id):
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = session["user_id"]
    try:
        result = _svc.update_interview(interview_id, user_id, data)
        return jsonify({"success": True, "message": "Interview updated.", "data": result}), 200
    except (InterviewNotFoundError, UnauthorizedError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
