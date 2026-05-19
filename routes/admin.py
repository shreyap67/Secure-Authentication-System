"""
routes/admin.py — Admin management + analytics API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from middleware.decorators import admin_required
from services import user_service

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/users")
@jwt_required()
@admin_required
def list_users():
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search   = request.args.get("search","").strip() or None
    result   = user_service.get_all_users(page=page, per_page=per_page, search=search)
    return jsonify({"success": True, **result}), 200


@admin_bp.get("/users/<int:user_id>")
@jwt_required()
@admin_required
def get_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404
    return jsonify({"success": True, "user": user.to_dict(include_sensitive=True)}), 200


@admin_bp.put("/users/<int:user_id>")
@jwt_required()
@admin_required
def update_user(user_id):
    data   = request.get_json(silent=True) or {}
    result = user_service.admin_update_user(int(get_jwt_identity()), user_id, data)
    return jsonify(result), 200 if result["success"] else 400


@admin_bp.delete("/users/<int:user_id>")
@jwt_required()
@admin_required
def delete_user(user_id):
    result = user_service.admin_delete_user(int(get_jwt_identity()), user_id)
    return jsonify(result), 200 if result["success"] else 400


@admin_bp.get("/stats")
@jwt_required()
@admin_required
def stats():
    data = user_service.get_admin_stats()
    return jsonify({"success": True, **data}), 200


@admin_bp.get("/analytics")
@jwt_required()
@admin_required
def analytics():
    """Rich analytics data for charts."""
    data = user_service.get_analytics_data()
    return jsonify({"success": True, **data}), 200


@admin_bp.get("/audit-logs")
@jwt_required()
@admin_required
def audit_logs():
    from models.user import AuditLog
    page = request.args.get("page", 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False)
    return jsonify({
        "success": True,
        "logs": [l.to_dict() for l in logs.items],
        "total": logs.total, "pages": logs.pages,
    }), 200


@admin_bp.get("/login-history")
@jwt_required()
@admin_required
def login_history():
    from models.user import LoginHistory
    page = request.args.get("page", 1, type=int)
    history = LoginHistory.query.order_by(LoginHistory.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False)
    return jsonify({
        "success": True,
        "history": [h.to_dict() for h in history.items],
        "total": history.total, "pages": history.pages,
    }), 200
