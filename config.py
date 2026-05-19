"""
config.py — Application Configuration
Secure Authentication & User Management Platform
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration — shared across all environments."""

    # ── Core Flask ─────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change-me-in-production"
    WTF_CSRF_ENABLED = True

    # ── Database ───────────────────────────────────────────────────────────────
    # Uses SQLite by default — no installation required.
    # To switch to PostgreSQL, set DATABASE_URL in your .env file.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///securehub.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ── JWT ────────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 900))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 604800))
    )
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False  # Set True in production (HTTPS only)
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"

    # ── Bcrypt ─────────────────────────────────────────────────────────────────
    BCRYPT_LOG_ROUNDS = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))

    # ── Rate Limiting ──────────────────────────────────────────────────────────
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")

    # ── Mail ───────────────────────────────────────────────────────────────────
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # ── Security ───────────────────────────────────────────────────────────────
    MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", 5))
    LOCKOUT_DURATION = int(os.environ.get("LOCKOUT_DURATION", 900))  # seconds

    # ── Admin Seed ─────────────────────────────────────────────────────────────
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@securehub.io")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@SecureHub123!")


class DevelopmentConfig(Config):
    DEBUG = True
    JWT_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_SECURE = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
