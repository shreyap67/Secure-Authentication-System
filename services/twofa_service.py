"""
services/twofa_service.py — TOTP Two-Factor Authentication
"""

import pyotp
import qrcode
import secrets
import json
import base64
import io
import logging
from datetime import datetime, timezone

from database import db, bcrypt
from models.user import User, AuditLog
from flask import request

logger = logging.getLogger(__name__)


def generate_totp_secret() -> str:
    """Generate a new random TOTP secret."""
    return pyotp.random_base32()


def get_totp_uri(user: User, secret: str) -> str:
    """Build the OTP auth URI for QR code generation."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="SecureHub"
    )


def generate_qr_code_base64(uri: str) -> str:
    """Generate QR code image and return as base64 PNG string."""
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#3b82f6", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def setup_2fa(user_id: int) -> dict:
    """Generate a new TOTP secret + QR code for setup. Does NOT enable 2FA yet."""
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "message": "User not found."}

    secret = generate_totp_secret()
    uri    = get_totp_uri(user, secret)
    qr_b64 = generate_qr_code_base64(uri)

    # Store secret temporarily (not yet enabled)
    user.totp_secret = secret
    db.session.commit()

    return {
        "success": True,
        "secret": secret,
        "qr_code": qr_b64,
        "uri": uri,
        "message": "Scan the QR code with Google Authenticator, then verify with a code to enable 2FA.",
    }


def verify_and_enable_2fa(user_id: int, totp_code: str) -> dict:
    """Verify TOTP code and enable 2FA if correct. Generates backup codes."""
    user = User.query.get(user_id)
    if not user or not user.totp_secret:
        return {"success": False, "message": "2FA setup not initiated."}

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(totp_code, valid_window=1):
        return {"success": False, "message": "Invalid verification code. Try again."}

    # Generate 8 backup codes
    raw_codes    = [secrets.token_hex(4).upper() + "-" + secrets.token_hex(4).upper() for _ in range(8)]
    hashed_codes = [bcrypt.generate_password_hash(c).decode("utf-8") for c in raw_codes]

    user.totp_enabled      = True
    user.totp_backup_codes = json.dumps(hashed_codes)
    _audit(user_id, "user.2fa.enabled", "user", str(user_id), "success", "2FA enabled")
    db.session.commit()

    logger.info(f"2FA enabled for user {user.email}")
    return {
        "success": True,
        "message": "2FA enabled successfully.",
        "backup_codes": raw_codes,
    }


def disable_2fa(user_id: int, password: str) -> dict:
    """Disable 2FA after verifying current password."""
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "message": "User not found."}
    if not bcrypt.check_password_hash(user.hashed_password, password):
        return {"success": False, "message": "Incorrect password."}

    user.totp_enabled      = False
    user.totp_secret       = None
    user.totp_backup_codes = None
    _audit(user_id, "user.2fa.disabled", "user", str(user_id), "warning", "2FA disabled")
    db.session.commit()

    return {"success": True, "message": "2FA has been disabled."}


def verify_totp_login(user: User, code: str) -> bool:
    """Verify a TOTP code or backup code during login."""
    if not user.totp_secret:
        return False

    # Check TOTP
    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(code, valid_window=1):
        return True

    # Check backup codes
    if user.totp_backup_codes:
        codes = json.loads(user.totp_backup_codes)
        for i, hashed in enumerate(codes):
            if bcrypt.check_password_hash(hashed, code.upper()):
                # Consume backup code (one-time use)
                codes.pop(i)
                user.totp_backup_codes = json.dumps(codes)
                _audit(user.id, "user.2fa.backup_code_used", "user", str(user.id),
                       "warning", "Backup code consumed")
                db.session.commit()
                return True
    return False


def _get_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def _audit(user_id, action, resource, resource_id, status, details):
    try:
        db.session.add(AuditLog(
            user_id=user_id, action=action, resource=resource,
            resource_id=resource_id, ip_address=_get_ip(),
            user_agent=request.headers.get("User-Agent", "")[:512],
            status=status, details=details,
        ))
    except Exception as e:
        logger.warning(f"Audit log error: {e}")
