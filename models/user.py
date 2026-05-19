"""
models/user.py — User, Role, Session, TokenBlacklist, AuditLog, LoginHistory
Extended with 2FA, OAuth, login history fields
"""

from datetime import datetime, timezone
from database import db
import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(db.Model):
    __tablename__ = "roles"
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class User(db.Model):
    __tablename__ = "users"

    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    email           = db.Column(db.String(255), unique=True, nullable=False, index=True)
    hashed_password = db.Column(db.String(255), nullable=True)  # nullable for OAuth users

    # Profile
    first_name  = db.Column(db.String(100))
    last_name   = db.Column(db.String(100))
    avatar_url  = db.Column(db.String(512))
    bio         = db.Column(db.Text)

    # Role
    role = db.Column(db.String(20), nullable=False, default=RoleEnum.USER.value)

    # Account State
    is_active           = db.Column(db.Boolean, default=True,  nullable=False)
    is_verified         = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at   = db.Column(db.DateTime(timezone=True))
    verification_token  = db.Column(db.String(255))

    # ── 2FA ──────────────────────────────────────────────────────────
    totp_secret         = db.Column(db.String(64))
    totp_enabled        = db.Column(db.Boolean, default=False, nullable=False)
    totp_backup_codes   = db.Column(db.Text)        # JSON array of hashed backup codes

    # ── OAuth ─────────────────────────────────────────────────────────
    oauth_provider      = db.Column(db.String(50))  # 'google', 'github', etc.
    oauth_id            = db.Column(db.String(255))  # provider user id
    oauth_token         = db.Column(db.Text)

    # Security / brute-force
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until          = db.Column(db.DateTime(timezone=True))
    last_login_at         = db.Column(db.DateTime(timezone=True))
    last_login_ip         = db.Column(db.String(45))
    password_changed_at   = db.Column(db.DateTime(timezone=True))
    reset_password_token  = db.Column(db.String(255))
    reset_password_expires= db.Column(db.DateTime(timezone=True))

    # Theme preference
    theme_preference = db.Column(db.String(10), default="dark")

    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    roles       = db.relationship("Role", secondary=user_roles, lazy="subquery",
                                  backref=db.backref("users", lazy="dynamic"))
    sessions    = db.relationship("UserSession",  back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    audit_logs  = db.relationship("AuditLog",     back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    login_history = db.relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def is_admin(self):
        return self.role == RoleEnum.ADMIN.value

    @property
    def is_locked(self):
        if self.locked_until:
            return datetime.now(timezone.utc) < self.locked_until
        return False

    @property
    def full_name(self):
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.username

    def to_dict(self, include_sensitive=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "totp_enabled": self.totp_enabled,
            "oauth_provider": self.oauth_provider,
            "theme_preference": self.theme_preference,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
        if include_sensitive:
            data["last_login_ip"]          = self.last_login_ip
            data["failed_login_attempts"]  = self.failed_login_attempts
            data["is_locked"]              = self.is_locked
        return data


class UserSession(db.Model):
    __tablename__ = "user_sessions"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = db.Column(db.String(512), unique=True, nullable=False, index=True)
    ip_address    = db.Column(db.String(45))
    user_agent    = db.Column(db.String(512))
    device_info   = db.Column(db.String(255))
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at    = db.Column(db.DateTime(timezone=True))
    last_activity = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="sessions")

    def to_dict(self):
        return {
            "id": self.id, "ip_address": self.ip_address,
            "device_info": self.device_info, "is_active": self.is_active,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"
    id         = db.Column(db.Integer, primary_key=True)
    jti        = db.Column(db.String(36), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(20), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    revoked_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True))


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action      = db.Column(db.String(100), nullable=False)
    resource    = db.Column(db.String(100))
    resource_id = db.Column(db.String(50))
    ip_address  = db.Column(db.String(45))
    user_agent  = db.Column(db.String(512))
    status      = db.Column(db.String(20), default="success")
    details     = db.Column(db.Text)
    created_at  = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="audit_logs")

    def to_dict(self):
        return {
            "id": self.id, "user_id": self.user_id, "action": self.action,
            "resource": self.resource, "ip_address": self.ip_address,
            "status": self.status, "details": self.details,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LoginHistory(db.Model):
    """Dedicated login history — every login attempt recorded."""
    __tablename__ = "login_history"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address  = db.Column(db.String(45))
    user_agent  = db.Column(db.String(512))
    device_type = db.Column(db.String(50))   # desktop / mobile / tablet
    browser     = db.Column(db.String(100))
    os          = db.Column(db.String(100))
    status      = db.Column(db.String(20), default="success")  # success / failure / 2fa_required
    failure_reason = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="login_history")

    def to_dict(self):
        return {
            "id": self.id, "ip_address": self.ip_address,
            "device_type": self.device_type, "browser": self.browser,
            "os": self.os, "status": self.status,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
