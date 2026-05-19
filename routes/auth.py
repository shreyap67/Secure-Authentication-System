"""
routes/auth.py — Authentication API blueprint (extended with 2FA)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt,
    create_access_token, verify_jwt_in_request,
)

from middleware import limiter
from middleware.decorators import active_user_required
from services import auth_service
from services.twofa_service import setup_2fa, verify_and_enable_2fa, disable_2fa
from utils.validators import validate_email_address, validate_username

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ── Register ───────────────────────────────────────────────────────────────────
@auth_bp.post("/register")
@limiter.limit("10 per hour")
def register():
    data       = request.get_json(silent=True) or {}
    username   = data.get("username","").strip()
    email      = data.get("email","").strip()
    password   = data.get("password","")
    first_name = data.get("first_name","").strip()
    last_name  = data.get("last_name","").strip()

    if not all([username, email, password]):
        return jsonify({"success": False, "message": "username, email, and password are required."}), 400

    uv = validate_username(username)
    if not uv["valid"]:
        return jsonify({"success": False, "message": uv["message"]}), 400

    ev = validate_email_address(email)
    if not ev["valid"]:
        return jsonify({"success": False, "message": ev["message"]}), 400

    result = auth_service.register_user(username=username, email=email, password=password,
                                        first_name=first_name or None, last_name=last_name or None)
    return jsonify(result), 201 if result["success"] else 409


# ── Login ──────────────────────────────────────────────────────────────────────
@auth_bp.post("/login")
@limiter.limit("20 per hour")
def login():
    data       = request.get_json(silent=True) or {}
    identifier = data.get("identifier","").strip()
    password   = data.get("password","")

    if not identifier or not password:
        return jsonify({"success": False, "message": "Email/username and password are required."}), 400

    result = auth_service.login_user(identifier=identifier, password=password)
    return jsonify(result), 200 if result["success"] else 401


# ── 2FA Verify (during login) ──────────────────────────────────────────────────
@auth_bp.post("/2fa/verify-login")
@limiter.limit("10 per hour")
def verify_2fa_login():
    """Complete login by verifying TOTP code with partial token."""
    data       = request.get_json(silent=True) or {}
    totp_code  = data.get("code","").strip()
    partial_token = data.get("partial_token","").strip()

    if not totp_code or not partial_token:
        return jsonify({"success": False, "message": "Code and partial token are required."}), 400

    # Decode partial token manually
    try:
        from flask_jwt_extended import decode_token
        decoded  = decode_token(partial_token)
        claims   = decoded.get("sub") or decoded.get("identity")
        add      = decoded.get("type","")
        user_id  = decoded.get("sub") or decoded.get("identity")
        # Check type claim
        if decoded.get("type") != "2fa_pending":
            return jsonify({"success": False, "message": "Invalid token type."}), 401
        user_id = decoded.get("sub")
    except Exception:
        return jsonify({"success": False, "message": "Invalid or expired partial token."}), 401

    result = auth_service.complete_2fa_login(user_id, totp_code)
    return jsonify(result), 200 if result["success"] else 401


# ── Logout ─────────────────────────────────────────────────────────────────────
@auth_bp.post("/logout")
@jwt_required()
def logout():
    jti     = get_jwt()["jti"]
    user_id = get_jwt_identity()
    result  = auth_service.logout_user(jti=jti, user_id=user_id)
    return jsonify(result), 200


# ── Refresh ────────────────────────────────────────────────────────────────────
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    claims  = get_jwt()
    new_token = create_access_token(
        identity=user_id,
        additional_claims={"role": claims.get("role"), "email": claims.get("email"), "username": claims.get("username")},
    )
    return jsonify({"success": True, "access_token": new_token}), 200


# ── Me ─────────────────────────────────────────────────────────────────────────
@auth_bp.get("/me")
@jwt_required()
@active_user_required
def me():
    from models.user import User
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404
    return jsonify({"success": True, "user": user.to_dict(include_sensitive=True)}), 200


# ── Email Verification ─────────────────────────────────────────────────────────
@auth_bp.get("/verify-email/<token>")
def verify_email(token):
    result = auth_service.verify_email(token)
    return jsonify(result), 200 if result["success"] else 400


# ── Forgot Password ────────────────────────────────────────────────────────────
@auth_bp.post("/forgot-password")
@limiter.limit("5 per hour")
def forgot_password():
    data  = request.get_json(silent=True) or {}
    email = data.get("email","").strip()
    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400
    return jsonify(auth_service.request_password_reset(email)), 200


# ── Reset Password ─────────────────────────────────────────────────────────────
@auth_bp.post("/reset-password")
@limiter.limit("5 per hour")
def reset_password():
    data         = request.get_json(silent=True) or {}
    token        = data.get("token","").strip()
    new_password = data.get("password","")
    if not token or not new_password:
        return jsonify({"success": False, "message": "Token and password are required."}), 400
    result = auth_service.reset_password(token, new_password)
    return jsonify(result), 200 if result["success"] else 400


# ── 2FA Setup ──────────────────────────────────────────────────────────────────
@auth_bp.post("/2fa/setup")
@jwt_required()
@active_user_required
def setup_2fa_route():
    result = setup_2fa(int(get_jwt_identity()))
    return jsonify(result), 200 if result["success"] else 400


@auth_bp.post("/2fa/enable")
@jwt_required()
@active_user_required
def enable_2fa():
    data = request.get_json(silent=True) or {}
    code = data.get("code","").strip()
    if not code:
        return jsonify({"success": False, "message": "TOTP code is required."}), 400
    result = verify_and_enable_2fa(int(get_jwt_identity()), code)
    return jsonify(result), 200 if result["success"] else 400


@auth_bp.post("/2fa/disable")
@jwt_required()
@active_user_required
def disable_2fa_route():
    data     = request.get_json(silent=True) or {}
    password = data.get("password","")
    if not password:
        return jsonify({"success": False, "message": "Password is required."}), 400
    result = disable_2fa(int(get_jwt_identity()), password)
    return jsonify(result), 200 if result["success"] else 400
