"""
Web routes for authentication (register, login, logout).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import AuthService
from app.exceptions.app_exceptions import (
    UserAlreadyExistsError, InvalidCredentialsError, ValidationError
)

auth_bp = Blueprint("auth", __name__)
_auth_service = AuthService()


@auth_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.home"))
    return render_template("home.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.home"))
    role = request.args.get("role", "candidate").upper()
    if request.method == "POST":
        role = request.form.get("role", "CANDIDATE").upper()
        try:
            if role == "RECRUITER":
                _auth_service.register_recruiter(request.form.to_dict())
            else:
                _auth_service.register_candidate(request.form.to_dict())
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except UserAlreadyExistsError as e:
            flash(e.message, "danger")
        except ValidationError as e:
            flash(e.message, "danger")
        except Exception as e:
            flash("Registration failed. Please try again.", "danger")
    return render_template("auth/register.html", role=role)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            _auth_service.login(email, password)
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("dashboard.home"))
        except InvalidCredentialsError as e:
            flash(e.message, "danger")
        except Exception:
            flash("Login failed. Please try again.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    _auth_service.logout()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
