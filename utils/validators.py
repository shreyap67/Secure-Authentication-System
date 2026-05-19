"""
utils/validators.py — Input validation and sanitization
"""

import re
import bleach
from email_validator import validate_email, EmailNotValidError


def sanitize_input(value: str) -> str:
    """Strip HTML tags and dangerous characters using bleach."""
    if not value:
        return ""
    cleaned = bleach.clean(str(value).strip(), tags=[], strip=True)
    return cleaned


def validate_email_address(email: str) -> dict:
    """Validate email format using email-validator library."""
    try:
        valid = validate_email(email, check_deliverability=False)
        return {"valid": True, "email": valid.normalized}
    except EmailNotValidError as e:
        return {"valid": False, "message": str(e)}


def validate_password_strength(password: str) -> dict:
    """
    Enforce enterprise-grade password policy:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return {"valid": False, "message": "Password must be at least 8 characters long."}
    if len(password) > 128:
        return {"valid": False, "message": "Password must not exceed 128 characters."}
    if not re.search(r"[A-Z]", password):
        return {"valid": False, "message": "Password must contain at least one uppercase letter."}
    if not re.search(r"[a-z]", password):
        return {"valid": False, "message": "Password must contain at least one lowercase letter."}
    if not re.search(r"\d", password):
        return {"valid": False, "message": "Password must contain at least one number."}
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;'/`~]", password):
        return {"valid": False, "message": "Password must contain at least one special character."}

    # Check common passwords (minimal list for illustration)
    common = {"password", "password1", "Password1!", "123456789", "qwerty123"}
    if password.lower() in common:
        return {"valid": False, "message": "Password is too common. Choose a stronger password."}

    return {"valid": True, "message": "Password meets requirements."}


def validate_username(username: str) -> dict:
    """Username: 3-30 chars, alphanumeric + underscore/hyphen, no spaces."""
    if not username or len(username) < 3:
        return {"valid": False, "message": "Username must be at least 3 characters."}
    if len(username) > 30:
        return {"valid": False, "message": "Username must not exceed 30 characters."}
    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        return {"valid": False, "message": "Username may only contain letters, numbers, underscores, and hyphens."}
    return {"valid": True}
