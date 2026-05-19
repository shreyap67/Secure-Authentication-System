"""
middleware/decorators.py — Role-based access control decorators
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from models.user import User


def roles_required(*roles):
    """Decorator: require authenticated user to have one of the specified roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "")
            if user_role not in roles:
                return jsonify({
                    "success": False,
                    "message": "Insufficient permissions. Access denied."
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator: restrict endpoint to admin users only."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({
                "success": False,
                "message": "Admin access required."
            }), 403
        return fn(*args, **kwargs)
    return wrapper


def active_user_required(fn):
    """Decorator: ensure authenticated user is active and not locked."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({"success": False, "message": "User not found."}), 404
        if not user.is_active:
            return jsonify({"success": False, "message": "Account is disabled."}), 403
        if user.is_locked:
            return jsonify({"success": False, "message": "Account is temporarily locked."}), 423

        return fn(*args, **kwargs)
    return wrapper
