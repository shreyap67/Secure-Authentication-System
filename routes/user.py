"""
routes/user.py — User profile API (extended with login history, theme)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from middleware.decorators import active_user_required
from services import user_service

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.get("/profile")
@jwt_required()
@active_user_required
def get_profile():
    user = user_service.get_user_by_id(int(get_jwt_identity()))
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404
    return jsonify({"success": True, "user": user.to_dict(include_sensitive=True)}), 200


@user_bp.put("/profile")
@jwt_required()
@active_user_required
def update_profile():
    data   = request.get_json(silent=True) or {}
    result = user_service.update_profile(int(get_jwt_identity()), data)
    return jsonify(result), 200 if result["success"] else 400


@user_bp.post("/change-password")
@jwt_required()
@active_user_required
def change_password():
    data             = request.get_json(silent=True) or {}
    current_password = data.get("current_password","")
    new_password     = data.get("new_password","")
    if not current_password or not new_password:
        return jsonify({"success": False, "message": "Both passwords are required."}), 400
    result = user_service.change_password(int(get_jwt_identity()), current_password, new_password)
    return jsonify(result), 200 if result["success"] else 400


@user_bp.get("/sessions")
@jwt_required()
@active_user_required
def get_sessions():
    from models.user import UserSession
    user_id  = int(get_jwt_identity())
    sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify({"success": True, "sessions": [s.to_dict() for s in sessions]}), 200


@user_bp.get("/audit-logs")
@jwt_required()
@active_user_required
def get_audit_logs():
    from models.user import AuditLog
    user_id = int(get_jwt_identity())
    page    = request.args.get("page", 1, type=int)
    logs    = (AuditLog.query.filter_by(user_id=user_id)
               .order_by(AuditLog.created_at.desc())
               .paginate(page=page, per_page=20, error_out=False))
    return jsonify({
        "success": True,
        "logs": [l.to_dict() for l in logs.items],
        "total": logs.total, "pages": logs.pages, "current_page": page,
    }), 200


@user_bp.get("/login-history")
@jwt_required()
@active_user_required
def get_login_history():
    from models.user import LoginHistory
    user_id = int(get_jwt_identity())
    page    = request.args.get("page", 1, type=int)
    history = (LoginHistory.query.filter_by(user_id=user_id)
               .order_by(LoginHistory.created_at.desc())
               .paginate(page=page, per_page=20, error_out=False))
    return jsonify({
        "success": True,
        "history": [h.to_dict() for h in history.items],
        "total": history.total, "pages": history.pages, "current_page": page,
    }), 200


@user_bp.put("/theme")
@jwt_required()
@active_user_required
def update_theme():
    data  = request.get_json(silent=True) or {}
    theme = data.get("theme","dark")
    if theme not in ["dark","light"]:
        return jsonify({"success": False, "message": "Invalid theme."}), 400
    from models.user import User
    from database import db
    user = User.query.get(int(get_jwt_identity()))
    user.theme_preference = theme
    db.session.commit()
    return jsonify({"success": True, "theme": theme}), 200
