"""
services/auth_service.py — Core authentication business logic
Extended with 2FA verification, login history, OAuth support
"""

import secrets
import logging
from datetime import datetime, timezone, timedelta

from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token

from database import db, bcrypt
from models.user import User, Role, TokenBlacklist, AuditLog, LoginHistory, RoleEnum
from utils.validators import validate_password_strength, sanitize_input

logger = logging.getLogger(__name__)


# ── Registration ───────────────────────────────────────────────────────────────

def register_user(username, email, password, first_name=None, last_name=None):
    username = sanitize_input(username)
    email    = sanitize_input(email).lower()

    if User.query.filter_by(email=email).first():
        return {"success": False, "message": "An account with this email already exists."}
    if User.query.filter_by(username=username).first():
        return {"success": False, "message": "Username is already taken."}

    strength = validate_password_strength(password)
    if not strength["valid"]:
        return {"success": False, "message": strength["message"]}

    hashed             = bcrypt.generate_password_hash(password, rounds=current_app.config["BCRYPT_LOG_ROUNDS"]).decode("utf-8")
    verification_token = secrets.token_urlsafe(32)

    user = User(
        username=username, email=email, hashed_password=hashed,
        first_name=sanitize_input(first_name) if first_name else None,
        last_name=sanitize_input(last_name)   if last_name  else None,
        role=RoleEnum.USER.value,
        verification_token=verification_token, is_verified=False,
    )
    db.session.add(user)
    db.session.flush()
    _audit(user.id, "user.register", "user", str(user.id), "success", f"Account created for {email}")
    db.session.commit()
    logger.info(f"New user registered: {email}")

    return {
        "success": True, "message": "Account created successfully.",
        "user": user.to_dict(), "verification_token": verification_token,
    }


# ── Login ──────────────────────────────────────────────────────────────────────

def login_user(identifier, password):
    identifier = sanitize_input(identifier).lower()
    ip         = _get_ip()
    ua         = request.headers.get("User-Agent", "")

    user = (User.query.filter_by(email=identifier).first()
            or User.query.filter_by(username=identifier).first())

    if not user:
        _audit(None, "user.login.failed", "auth", None, "failure", f"No account: {identifier}")
        return {"success": False, "message": "Invalid credentials."}

    if user.is_locked:
        remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() // 60) + 1
        return {"success": False, "message": f"Account locked. Try again in {remaining} minute(s)."}

    if not user.is_active:
        return {"success": False, "message": "Account is disabled. Contact support."}

    if not user.hashed_password:
        return {"success": False, "message": "This account uses social login. Please sign in with Google."}

    if not bcrypt.check_password_hash(user.hashed_password, password):
        user.failed_login_attempts += 1
        max_attempts = current_app.config["MAX_LOGIN_ATTEMPTS"]

        _record_login_history(user.id, ip, ua, "failure", "Wrong password")

        if user.failed_login_attempts >= max_attempts:
            lockout = current_app.config["LOCKOUT_DURATION"]
            user.locked_until = datetime.now(timezone.utc) + timedelta(seconds=lockout)
            _audit(user.id, "user.account.locked", "user", str(user.id), "warning",
                   f"Locked after {max_attempts} failed attempts")
            db.session.commit()
            return {"success": False, "message": f"Too many failed attempts. Account locked for {lockout // 60} minutes."}

        db.session.commit()
        remaining = max_attempts - user.failed_login_attempts
        return {"success": False, "message": f"Invalid credentials. {remaining} attempt(s) remaining."}

    # ── 2FA check ──────────────────────────────────────────────────
    if user.totp_enabled:
        # Return partial token indicating 2FA required
        partial_token = create_access_token(
            identity=str(user.id),
            additional_claims={"type": "2fa_pending", "email": user.email},
            expires_delta=timedelta(minutes=5),
        )
        return {
            "success": True,
            "requires_2fa": True,
            "partial_token": partial_token,
            "message": "2FA verification required.",
        }

    return _complete_login(user, ip, ua)


def complete_2fa_login(user_id, totp_code):
    """Complete login after successful 2FA verification."""
    from services.twofa_service import verify_totp_login
    user = User.query.get(int(user_id))
    if not user:
        return {"success": False, "message": "User not found."}

    if not verify_totp_login(user, totp_code):
        _record_login_history(user.id, _get_ip(), request.headers.get("User-Agent",""), "failure", "Bad 2FA code")
        return {"success": False, "message": "Invalid 2FA code."}

    return _complete_login(user, _get_ip(), request.headers.get("User-Agent", ""))


def _complete_login(user, ip, ua):
    """Finalize login — reset counters, create tokens, record history."""
    user.failed_login_attempts = 0
    user.locked_until          = None
    user.last_login_at         = datetime.now(timezone.utc)
    user.last_login_ip         = ip

    claims = {"role": user.role, "email": user.email, "username": user.username}
    access_token  = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)

    _record_login_history(user.id, ip, ua, "success", None)
    _audit(user.id, "user.login", "auth", str(user.id), "success", f"Login from {ip}")
    db.session.commit()
    logger.info(f"User logged in: {user.email}")

    return {
        "success": True, "requires_2fa": False,
        "message": "Login successful.",
        "access_token": access_token, "refresh_token": refresh_token,
        "user": user.to_dict(),
    }


# ── Logout ─────────────────────────────────────────────────────────────────────

def logout_user(jti, user_id):
    db.session.add(TokenBlacklist(
        jti=jti, token_type="access", user_id=int(user_id),
        expires_at=datetime.now(timezone.utc) + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    ))
    _audit(int(user_id), "user.logout", "auth", user_id, "success", "Token blacklisted")
    db.session.commit()
    return {"success": True, "message": "Logged out successfully."}


# ── Password Reset ─────────────────────────────────────────────────────────────

def request_password_reset(email):
    email = sanitize_input(email).lower()
    user  = User.query.filter_by(email=email).first()
    if not user:
        return {"success": True, "message": "If that email exists, a reset link has been sent."}

    token = secrets.token_urlsafe(48)
    user.reset_password_token   = token
    user.reset_password_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    _audit(user.id, "user.password_reset.requested", "user", str(user.id), "success", "")
    db.session.commit()
    return {
        "success": True, "message": "If that email exists, a reset link has been sent.",
        "token": token, "user_email": user.email,
    }


def reset_password(token, new_password):
    user = User.query.filter_by(reset_password_token=token).first()
    if not user:
        return {"success": False, "message": "Invalid or expired reset token."}
    if not user.reset_password_expires or datetime.now(timezone.utc) > user.reset_password_expires:
        return {"success": False, "message": "Reset token has expired."}

    strength = validate_password_strength(new_password)
    if not strength["valid"]:
        return {"success": False, "message": strength["message"]}

    user.hashed_password        = bcrypt.generate_password_hash(new_password, rounds=current_app.config["BCRYPT_LOG_ROUNDS"]).decode("utf-8")
    user.reset_password_token   = None
    user.reset_password_expires = None
    user.password_changed_at    = datetime.now(timezone.utc)
    _audit(user.id, "user.password.reset", "user", str(user.id), "success", "Password reset")
    db.session.commit()
    return {"success": True, "message": "Password reset successfully."}


# ── Email Verification ─────────────────────────────────────────────────────────

def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return {"success": False, "message": "Invalid verification token."}
    if user.is_verified:
        return {"success": True, "message": "Email already verified."}

    user.is_verified         = True
    user.email_verified_at   = datetime.now(timezone.utc)
    user.verification_token  = None
    _audit(user.id, "user.email.verified", "user", str(user.id), "success", "")
    db.session.commit()
    return {"success": True, "message": "Email verified successfully."}


# ── OAuth User ─────────────────────────────────────────────────────────────────

def get_or_create_oauth_user(email, name, provider, oauth_id, avatar_url=None):
    """Find or create a user from OAuth provider data."""
    user = User.query.filter_by(email=email).first()

    if user:
        # Update OAuth fields if not set
        user.oauth_provider = provider
        user.oauth_id       = oauth_id
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
    else:
        # Create new user
        parts    = (name or email.split("@")[0]).split(" ", 1)
        username = email.split("@")[0] + secrets.token_hex(2)
        user = User(
            username=username, email=email,
            hashed_password=None,
            first_name=parts[0], last_name=parts[1] if len(parts) > 1 else None,
            role=RoleEnum.USER.value,
            is_verified=True, is_active=True,
            oauth_provider=provider, oauth_id=oauth_id,
            avatar_url=avatar_url,
        )
        db.session.add(user)

    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = _get_ip()
    db.session.commit()
    return user


# ── Helpers ────────────────────────────────────────────────────────────────────

def is_token_blacklisted(jti):
    return TokenBlacklist.query.filter_by(jti=jti).first() is not None


def _record_login_history(user_id, ip, ua_string, status, reason):
    try:
        device_type = "desktop"
        browser     = "Unknown"
        os_name     = "Unknown"
        try:
            import user_agents
            ua = user_agents.parse(ua_string)
            browser     = f"{ua.browser.family} {ua.browser.version_string}"
            os_name     = f"{ua.os.family} {ua.os.version_string}"
            if ua.is_mobile:   device_type = "mobile"
            elif ua.is_tablet: device_type = "tablet"
        except Exception:
            pass

        db.session.add(LoginHistory(
            user_id=user_id, ip_address=ip,
            user_agent=ua_string[:512] if ua_string else None,
            device_type=device_type, browser=browser[:100], os=os_name[:100],
            status=status, failure_reason=reason,
        ))
    except Exception as e:
        logger.warning(f"Login history error: {e}")


def _get_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def _audit(user_id, action, resource, resource_id, status, details):
    try:
        db.session.add(AuditLog(
            user_id=user_id, action=action, resource=resource, resource_id=resource_id,
            ip_address=_get_ip(), user_agent=request.headers.get("User-Agent","")[:512],
            status=status, details=details,
        ))
    except Exception as e:
        logger.warning(f"Audit log error: {e}")
