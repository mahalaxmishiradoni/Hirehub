"""
Reusable authentication and authorisation decorators.
"""
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from app.exceptions.app_exceptions import UnauthorizedError


def _wants_json() -> bool:
    return request.path.startswith("/api/") or request.is_json


def login_required(f):
    """Ensure user is logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if _wants_json():
                return jsonify({"success": False, "message": "Authentication required.", "error_code": "UNAUTHENTICATED"}), 401
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Ensure the current user has one of the required roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                if _wants_json():
                    return jsonify({"success": False, "message": "Authentication required.", "error_code": "UNAUTHENTICATED"}), 401
                return redirect(url_for("auth.login", next=request.url))
            user_role = session.get("role", "")
            if user_role not in roles:
                if _wants_json():
                    return jsonify({"success": False, "message": "You do not have permission.", "error_code": "UNAUTHORIZED"}), 403
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def candidate_required(f):
    return role_required("CANDIDATE")(f)


def recruiter_required(f):
    return role_required("RECRUITER")(f)


def admin_required(f):
    return role_required("ADMIN")(f)
