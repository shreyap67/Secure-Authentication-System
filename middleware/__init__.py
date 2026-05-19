"""
middleware/__init__.py — JWT callbacks, security headers, CORS, request hooks
"""

import logging
from flask import jsonify, request, g
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)

jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def init_middleware(app):
    """Register all middleware with the Flask app."""
    jwt.init_app(app)
    limiter.init_app(app)

    # ── JWT Callbacks ──────────────────────────────────────────────────────────

    @jwt.token_in_blocklist_loader
    def check_token_blacklist(jwt_header, jwt_payload):
        from services.auth_service import is_token_blacklisted
        return is_token_blacklisted(jwt_payload["jti"])

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has been revoked. Please log in again."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has expired. Please refresh your session."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"success": False, "message": "Invalid token."}), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"success": False, "message": "Authentication required."}), 401

    # ── Security Headers ───────────────────────────────────────────────────────

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        return response

    # ── Request Logging ────────────────────────────────────────────────────────

    @app.before_request
    def log_request():
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        logger.debug(f"→ {request.method} {request.path} from {ip}")
