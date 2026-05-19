"""
app.py — Secure Authentication & User Management Platform (Enterprise Edition)
Run: python app.py
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import config_map
from database import init_db, db
from middleware import init_middleware
from utils import setup_logging


def create_app(env: str = None) -> Flask:
    env = env or os.environ.get("FLASK_ENV", "development")
    cfg = config_map.get(env, config_map["default"])

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(cfg)

    setup_logging(app)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting SecureHub Enterprise in [{env}] mode")

    # ── Extensions ────────────────────────────────────────────────
    init_db(app)
    init_middleware(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Swagger / OpenAPI ─────────────────────────────────────────
    try:
        from flasgger import Swagger
        swagger_config = {
            "headers": [],
            "specs": [{"endpoint": "apispec", "route": "/api/spec.json",
                       "rule_filter": lambda rule: rule.rule.startswith("/api/"),
                       "model_filter": lambda tag: True}],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/api/docs",
        }
        swagger_template = {
            "info": {
                "title": "SecureHub API",
                "description": "Enterprise Authentication & User Management Platform",
                "version": "2.0.0",
                "contact": {"name": "SecureHub Team"},
            },
            "securityDefinitions": {
                "BearerAuth": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT Bearer token: Bearer <token>",
                }
            },
            "security": [{"BearerAuth": []}],
        }
        Swagger(app, config=swagger_config, template=swagger_template)
        logger.info("Swagger UI available at /api/docs")
    except Exception as e:
        logger.warning(f"Swagger init skipped: {e}")

    # ── Blueprints ────────────────────────────────────────────────
    from routes.auth  import auth_bp
    from routes.user  import user_bp
    from routes.admin import admin_bp
    from routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pages_bp)

    # ── Global Error Handlers ─────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "message": "Bad request."}), 400

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "message": "Method not allowed."}), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"success": False, "message": "Too many requests. Slow down."}), 429

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.exception(f"Unhandled exception: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500

    # ── Health ────────────────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "SecureHub Enterprise",
            "version": "2.0.0",
            "features": ["jwt", "2fa", "rbac", "audit-logging", "login-history", "analytics"],
        }), 200

    # ── DB Init & Seed ────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_database(app)

    return app


def _seed_database(app):
    from models.user import User, Role, RoleEnum
    from database import bcrypt
    logger = logging.getLogger(__name__)

    for role_name in [r.value for r in RoleEnum]:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name, description=f"{role_name.capitalize()} role"))
            logger.info(f"Seeded role: {role_name}")

    admin_email    = app.config["ADMIN_EMAIL"]
    admin_username = app.config["ADMIN_USERNAME"]
    admin_password = app.config["ADMIN_PASSWORD"]

    if not User.query.filter_by(email=admin_email).first():
        hashed = bcrypt.generate_password_hash(
            admin_password, rounds=app.config["BCRYPT_LOG_ROUNDS"]
        ).decode("utf-8")
        admin = User(
            username=admin_username, email=admin_email,
            hashed_password=hashed, role=RoleEnum.ADMIN.value,
            is_active=True, is_verified=True,
            first_name="SecureHub", last_name="Admin",
        )
        db.session.add(admin)
        logger.info(f"Seeded admin: {admin_email}")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.warning(f"Seed rollback: {e}")


# ── Entry Point ───────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║       SecureHub — Enterprise Authentication Platform v2      ║
╠══════════════════════════════════════════════════════════════╣
║  Server   : http://localhost:{port:<30}║
║  API Docs : http://localhost:{port}/api/docs                 ║
║  Health   : http://localhost:{port}/api/health               ║
╠══════════════════════════════════════════════════════════════╣
║  Features : JWT · 2FA · RBAC · Analytics · Audit Logging    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=debug)
