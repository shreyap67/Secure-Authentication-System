"""
services/user_service.py — User profile and admin management logic
"""

import logging
from datetime import datetime, timezone

from database import db, bcrypt
from models.user import User, AuditLog, RoleEnum
from utils.validators import validate_password_strength, sanitize_input
from flask import current_app, request

logger = logging.getLogger(__name__)


def get_user_by_id(user_id: int) -> User | None:
    return User.query.get(user_id)


def get_all_users(page: int = 1, per_page: int = 20, search: str = None):
    query = User.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            (User.username.ilike(like)) | (User.email.ilike(like))
        )
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return {
        "users": [u.to_dict(include_sensitive=True) for u in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
        "per_page": per_page,
    }


def update_profile(user_id: int, data: dict) -> dict:
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "message": "User not found."}

    allowed_fields = ["first_name", "last_name", "bio", "avatar_url"]
    for field in allowed_fields:
        if field in data:
            setattr(user, field, sanitize_input(str(data[field])) if data[field] else None)

    user.updated_at = datetime.now(timezone.utc)
    _audit(user_id, "user.profile.updated", "user", str(user_id), "success", "Profile fields updated")
    db.session.commit()
    return {"success": True, "message": "Profile updated.", "user": user.to_dict()}


def change_password(user_id: int, current_password: str, new_password: str) -> dict:
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "message": "User not found."}

    if not bcrypt.check_password_hash(user.hashed_password, current_password):
        _audit(user_id, "user.password.change.failed", "user", str(user_id), "failure", "Wrong current password")
        return {"success": False, "message": "Current password is incorrect."}

    strength = validate_password_strength(new_password)
    if not strength["valid"]:
        return {"success": False, "message": strength["message"]}

    user.hashed_password = bcrypt.generate_password_hash(
        new_password, rounds=current_app.config["BCRYPT_LOG_ROUNDS"]
    ).decode("utf-8")
    user.password_changed_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)

    _audit(user_id, "user.password.changed", "user", str(user_id), "success", "Password changed")
    db.session.commit()
    return {"success": True, "message": "Password changed successfully."}


def admin_update_user(admin_id: int, target_user_id: int, data: dict) -> dict:
    target = User.query.get(target_user_id)
    if not target:
        return {"success": False, "message": "User not found."}

    if "role" in data and data["role"] in [r.value for r in RoleEnum]:
        target.role = data["role"]
    if "is_active" in data:
        target.is_active = bool(data["is_active"])

    target.updated_at = datetime.now(timezone.utc)
    _audit(admin_id, "admin.user.updated", "user", str(target_user_id), "success",
           f"Admin updated user {target.email}")
    db.session.commit()
    return {"success": True, "message": "User updated.", "user": target.to_dict(include_sensitive=True)}


def admin_delete_user(admin_id: int, target_user_id: int) -> dict:
    target = User.query.get(target_user_id)
    if not target:
        return {"success": False, "message": "User not found."}
    if target_user_id == admin_id:
        return {"success": False, "message": "Cannot delete your own account."}

    email = target.email
    db.session.delete(target)
    _audit(admin_id, "admin.user.deleted", "user", str(target_user_id), "success",
           f"Admin deleted user {email}")
    db.session.commit()
    return {"success": True, "message": f"User {email} deleted."}


def get_admin_stats() -> dict:
    from sqlalchemy import func
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    verified_users = User.query.filter_by(is_verified=True).count()
    admin_users = User.query.filter_by(role=RoleEnum.ADMIN.value).count()
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "admin_users": admin_users,
        "recent_audit_logs": [l.to_dict() for l in recent_logs],
    }


def _get_ip() -> str:
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def _audit(user_id, action, resource, resource_id, status, details):
    try:
        log = AuditLog(
            user_id=user_id, action=action, resource=resource,
            resource_id=resource_id, ip_address=_get_ip(),
            user_agent=request.headers.get("User-Agent", "")[:512],
            status=status, details=details,
        )
        db.session.add(log)
    except Exception as e:
        logger.warning(f"Audit log error: {e}")


def get_analytics_data() -> dict:
    """Rich analytics data for admin dashboard charts."""
    from models.user import LoginHistory, AuditLog, RoleEnum
    from sqlalchemy import func
    from datetime import datetime, timezone, timedelta

    now  = datetime.now(timezone.utc)
    days = 30

    # User growth — registrations per day for last 30 days
    growth_data = []
    for i in range(days - 1, -1, -1):
        day_start = now - timedelta(days=i+1)
        day_end   = now - timedelta(days=i)
        count = User.query.filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).count()
        growth_data.append({
            "date": day_start.strftime("%b %d"),
            "count": count
        })

    # Login activity — logins per day last 14 days
    login_data = []
    for i in range(13, -1, -1):
        day_start = now - timedelta(days=i+1)
        day_end   = now - timedelta(days=i)
        success = LoginHistory.query.filter(
            LoginHistory.created_at >= day_start,
            LoginHistory.created_at < day_end,
            LoginHistory.status == "success"
        ).count()
        failed = LoginHistory.query.filter(
            LoginHistory.created_at >= day_start,
            LoginHistory.created_at < day_end,
            LoginHistory.status == "failure"
        ).count()
        login_data.append({
            "date": day_start.strftime("%b %d"),
            "success": success,
            "failed": failed
        })

    # Role distribution
    role_dist = []
    for role in RoleEnum:
        cnt = User.query.filter_by(role=role.value).count()
        role_dist.append({"role": role.value, "count": cnt})

    # Device breakdown
    device_data = []
    for dtype in ["desktop", "mobile", "tablet"]:
        cnt = LoginHistory.query.filter_by(device_type=dtype).count()
        device_data.append({"device": dtype, "count": cnt})

    # Top actions in audit log
    top_actions = db.session.execute(
        db.text("SELECT action, COUNT(*) as cnt FROM audit_logs GROUP BY action ORDER BY cnt DESC LIMIT 8")
    ).fetchall()

    # Recent failed logins (security alerts)
    recent_failures = (LoginHistory.query
                       .filter_by(status="failure")
                       .order_by(LoginHistory.created_at.desc())
                       .limit(5).all())

    # 2FA adoption
    twofa_enabled  = User.query.filter_by(totp_enabled=True).count()
    twofa_disabled = User.query.filter_by(totp_enabled=False).count()

    return {
        "user_growth":      growth_data,
        "login_activity":   login_data,
        "role_distribution": role_dist,
        "device_breakdown": device_data,
        "top_actions":      [{"action": r[0], "count": r[1]} for r in top_actions],
        "recent_failures":  [f.to_dict() for f in recent_failures],
        "twofa_stats":      {"enabled": twofa_enabled, "disabled": twofa_disabled},
    }
