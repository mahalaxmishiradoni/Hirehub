"""
REST API — admin management endpoints.
"""
from flask import Blueprint, request, jsonify, session
from app.repositories.user_repository import UserRepository
from app.services.company_service import CompanyService
from app.middleware.audit_middleware import AuditLogger
from app.utils.decorators import admin_required
from app.utils.helpers import serialize_doc

admin_api_bp = Blueprint("admin_api", __name__)
_users = UserRepository()
_company_svc = CompanyService()


@admin_api_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    role = request.args.get("role", "")
    filters = {"role": role} if role else {}
    result = _users.find_all(filters=filters, page=page, per_page=per_page)
    result["items"] = [serialize_doc(u) for u in result["items"]]
    return jsonify({"success": True, "message": "OK", "data": result}), 200


@admin_api_bp.route("/users/<user_id>/activate", methods=["PUT"])
@admin_required
def activate_user(user_id):
    _users.set_active(user_id, True)
    return jsonify({"success": True, "message": "User activated.", "data": {}}), 200


@admin_api_bp.route("/users/<user_id>/deactivate", methods=["PUT"])
@admin_required
def deactivate_user(user_id):
    _users.set_active(user_id, False)
    AuditLogger.log(session["user_id"], AuditLogger.USER_DEACTIVATED, "users", user_id)
    return jsonify({"success": True, "message": "User deactivated.", "data": {}}), 200


@admin_api_bp.route("/companies/<company_id>/verify", methods=["PUT"])
@admin_required
def verify_company(company_id):
    try:
        result = _company_svc.verify_company(company_id)
        return jsonify({"success": True, "message": "Company verified.", "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "ERROR"}), 400


@admin_api_bp.route("/audit-logs", methods=["GET"])
@admin_required
def audit_logs():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    action = request.args.get("action", "")
    filters = {"action": action} if action else {}
    result = AuditLogger.get_logs(page=page, per_page=per_page, filters=filters)
    result["items"] = [serialize_doc(l) for l in result["items"]]
    return jsonify({"success": True, "message": "OK", "data": result}), 200
