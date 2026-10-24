"""
REST API — job endpoints.
"""
from flask import Blueprint, request, jsonify, session
from app.services.job_service import JobService
from app.utils.decorators import login_required, recruiter_required
from app.exceptions.app_exceptions import JobNotFoundError, UnauthorizedError, ValidationError

job_api_bp = Blueprint("job_api", __name__)
_svc = JobService()


@job_api_bp.route("", methods=["GET"])
def list_jobs():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    filters = {k: v for k, v in request.args.items() if k not in ("page", "per_page")}
    result = _svc.search_jobs(filters, page=page, per_page=per_page)
    return jsonify({"success": True, "message": "OK", "data": result}), 200


@job_api_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = _svc.get_job(job_id)
        return jsonify({"success": True, "message": "OK", "data": job}), 200
    except JobNotFoundError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), 404


@job_api_bp.route("", methods=["POST"])
@recruiter_required
def create_job():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = session["user_id"]
    company_id = session.get("company_id", "")
    try:
        job = _svc.create_job(data, user_id, company_id)
        return jsonify({"success": True, "message": "Job created.", "data": job}), 201
    except ValidationError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), 422
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "SERVER_ERROR"}), 500


@job_api_bp.route("/<job_id>", methods=["PUT"])
@recruiter_required
def update_job(job_id):
    data = request.get_json(silent=True) or request.form.to_dict()
    user_id = session["user_id"]
    try:
        job = _svc.update_job(job_id, user_id, data)
        return jsonify({"success": True, "message": "Job updated.", "data": job}), 200
    except (JobNotFoundError, UnauthorizedError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
    except ValidationError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), 422


@job_api_bp.route("/<job_id>", methods=["DELETE"])
@recruiter_required
def delete_job(job_id):
    user_id = session["user_id"]
    try:
        _svc.delete_job(job_id, user_id)
        return jsonify({"success": True, "message": "Job deleted.", "data": {}}), 200
    except (JobNotFoundError, UnauthorizedError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code


@job_api_bp.route("/<job_id>/apply", methods=["POST"])
@login_required
def apply(job_id):
    from app.services.application_service import ApplicationService
    from app.exceptions.app_exceptions import DuplicateApplicationError, JobClosedError
    app_svc = ApplicationService()
    user_id = session["user_id"]
    profile_id = session.get("profile_id", "")
    try:
        result = app_svc.apply(profile_id, user_id, job_id)
        return jsonify({"success": True, "message": "Application submitted successfully.", "data": result}), 201
    except (DuplicateApplicationError, JobClosedError, JobNotFoundError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "SERVER_ERROR"}), 500
