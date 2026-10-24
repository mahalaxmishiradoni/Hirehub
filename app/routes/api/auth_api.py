"""
REST API — authentication endpoints.
"""
from flask import Blueprint, request, jsonify, session
from app.services.auth_service import AuthService
from app.utils.helpers import success_response, error_response
from app.utils.decorators import login_required
from app.exceptions.app_exceptions import UserAlreadyExistsError, InvalidCredentialsError, ValidationError

auth_api_bp = Blueprint("auth_api", __name__)
_svc = AuthService()


@auth_api_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form.to_dict()
    role = data.get("role", "CANDIDATE").upper()
    try:
        if role == "RECRUITER":
            result = _svc.register_recruiter(data)
        else:
            result = _svc.register_candidate(data)
        return jsonify({"success": True, "message": "Registration successful.", "data": result}), 201
    except (UserAlreadyExistsError, ValidationError) as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
    except Exception as e:
        return jsonify({"success": False, "message": "Registration failed.", "error_code": "SERVER_ERROR"}), 500


@auth_api_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form.to_dict()
    try:
        user = _svc.login(data.get("email", ""), data.get("password", ""))
        return jsonify({"success": True, "message": "Login successful.", "data": user}), 200
    except InvalidCredentialsError as e:
        return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
    except Exception:
        return jsonify({"success": False, "message": "Login failed.", "error_code": "SERVER_ERROR"}), 500


@auth_api_bp.route("/logout", methods=["POST"])
def logout():
    _svc.logout()
    return jsonify({"success": True, "message": "Logged out.", "data": {}}), 200


@auth_api_bp.route("/me", methods=["GET"])
@login_required
def me():
    try:
        user = _svc.get_current_user()
        return jsonify({"success": True, "message": "OK", "data": user}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error_code": "USER_NOT_FOUND"}), 404
