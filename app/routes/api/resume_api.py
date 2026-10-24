"""
REST API — resume endpoints.
"""
from flask import Blueprint, request, jsonify, session, send_file
from app.services.resume_service import ResumeService
from app.utils.decorators import login_required, candidate_required
from app.exceptions.app_exceptions import UnauthorizedError

resume_api_bp = Blueprint("resume_api", __name__)
_svc = ResumeService()


@resume_api_bp.route("", methods=["POST"])
@candidate_required
def upload_resume():
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    file = request.files.get("resume")
    try:
        result = _svc.upload_resume(file, profile_id, user_id)
        return jsonify({"success": True, "message": "Resume uploaded.", "data": result}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "RESUME_UPLOAD_ERROR"}), 400


@resume_api_bp.route("/<resume_id>", methods=["GET"])
@login_required
def get_resume(resume_id):
    user_id = session["user_id"]
    role = session.get("role", "CANDIDATE")
    try:
        doc = _svc.get_resume(resume_id, user_id, role)
        return jsonify({"success": True, "message": "OK", "data": doc}), 200
    except UnauthorizedError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), 403
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "NOT_FOUND"}), 404


@resume_api_bp.route("/<resume_id>", methods=["DELETE"])
@candidate_required
def delete_resume(resume_id):
    user_id = session["user_id"]
    try:
        _svc.delete_resume(resume_id, user_id)
        return jsonify({"success": True, "message": "Resume deleted.", "data": {}}), 200
    except UnauthorizedError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), 403
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "ERROR"}), 400
