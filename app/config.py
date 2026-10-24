"""
Application configuration using environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "fallback-secret-change-me")
    FLASK_ENV: str = os.environ.get("FLASK_ENV", "production")

    # MongoDB
    MONGO_URI: str = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DATABASE: str = os.environ.get("MONGO_DATABASE", "hirehub")

    # File uploads
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "app/uploads/resumes")
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    ALLOWED_EXTENSIONS: set = {"pdf", "doc", "docx"}

    # Session / Cookie
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_COOKIE_SECURE: bool = os.environ.get("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME: int = 3600 * 24 * 7  # 7 days

    # Pagination
    JOBS_PER_PAGE: int = 10
    USERS_PER_PAGE: int = 20


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True
    SESSION_COOKIE_SECURE: bool = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False
    SESSION_COOKIE_SECURE: bool = True


class TestingConfig(Config):
    """Testing configuration."""

    TESTING: bool = True
    DEBUG: bool = True
    MONGO_DATABASE: str = "hirehub_test"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_SAMESITE: str = "Lax"
    WTF_CSRF_ENABLED: bool = False
    # Prevent session.permanent from requiring SERVER_NAME in test context
    PERMANENT_SESSION_LIFETIME: int = 3600


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config() -> Config:
    """Return configuration object based on FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)()
