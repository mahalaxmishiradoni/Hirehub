"""
HireHub Application Factory.
"""
import os
from flask import Flask
from app.config import get_config
from app.extensions import mongo


def create_app(config=None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Load configuration
    cfg = config if config is not None else get_config()
    app.config.from_object(cfg)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    return app


def _register_blueprints(app: Flask) -> None:
    """Register all route blueprints."""
    from app.routes.web.auth_routes import auth_bp
    from app.routes.web.candidate_routes import candidate_bp
    from app.routes.web.recruiter_routes import recruiter_bp
    from app.routes.web.admin_routes import admin_bp
    from app.routes.web.job_routes import job_bp
    from app.routes.web.dashboard_routes import dashboard_bp
    from app.routes.api.auth_api import auth_api_bp
    from app.routes.api.candidate_api import candidate_api_bp
    from app.routes.api.recruiter_api import recruiter_api_bp
    from app.routes.api.job_api import job_api_bp
    from app.routes.api.application_api import application_api_bp
    from app.routes.api.interview_api import interview_api_bp
    from app.routes.api.resume_api import resume_api_bp
    from app.routes.api.analytics_api import analytics_api_bp
    from app.routes.api.admin_api import admin_api_bp

    # Web routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(dashboard_bp)

    # API routes
    app.register_blueprint(auth_api_bp, url_prefix="/api/auth")
    app.register_blueprint(candidate_api_bp, url_prefix="/api/candidates")
    app.register_blueprint(recruiter_api_bp, url_prefix="/api/recruiters")
    app.register_blueprint(job_api_bp, url_prefix="/api/jobs")
    app.register_blueprint(application_api_bp, url_prefix="/api/applications")
    app.register_blueprint(interview_api_bp, url_prefix="/api/interviews")
    app.register_blueprint(resume_api_bp, url_prefix="/api/resumes")
    app.register_blueprint(analytics_api_bp, url_prefix="/api/analytics")
    app.register_blueprint(admin_api_bp, url_prefix="/api/admin")


def _register_error_handlers(app: Flask) -> None:
    """Register centralized error handlers."""
    from flask import request, jsonify, render_template
    from app.exceptions.app_exceptions import (
        AppException,
        UserAlreadyExistsError,
        InvalidCredentialsError,
        UserNotFoundError,
        UnauthorizedError,
        JobNotFoundError,
        JobClosedError,
        DuplicateApplicationError,
        ApplicationNotFoundError,
        InvalidApplicationStatusError,
        ResumeUploadError,
        ValidationError,
    )

    def wants_json() -> bool:
        return request.path.startswith("/api/") or request.is_json

    @app.errorhandler(AppException)
    def handle_app_exception(e: AppException):
        if wants_json():
            return jsonify({"success": False, "message": e.message, "error_code": e.error_code}), e.status_code
        return render_template("errors/error.html", message=e.message, code=e.status_code), e.status_code

    @app.errorhandler(404)
    def not_found(e):
        if wants_json():
            return jsonify({"success": False, "message": "Resource not found", "error_code": "NOT_FOUND"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        if wants_json():
            return jsonify({"success": False, "message": "Forbidden", "error_code": "FORBIDDEN"}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        if wants_json():
            return jsonify({"success": False, "message": "Internal server error", "error_code": "INTERNAL_ERROR"}), 500
        return render_template("errors/500.html"), 500
