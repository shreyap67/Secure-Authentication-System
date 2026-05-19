"""
database/seed.py — Standalone seed script for development data
Run: python database/seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import db, bcrypt
from models.user import User, Role, RoleEnum
import logging

logger = logging.getLogger(__name__)


def seed_demo_users(app):
    """Create demo users for development testing."""
    demo_users = [
        {
            "username": "alice",
            "email": "alice@demo.com",
            "password": "Alice@Demo123!",
            "first_name": "Alice",
            "last_name": "Johnson",
            "role": RoleEnum.USER.value,
            "is_verified": True,
        },
        {
            "username": "bob",
            "email": "bob@demo.com",
            "password": "Bob@Demo123!",
            "first_name": "Bob",
            "last_name": "Smith",
            "role": RoleEnum.USER.value,
            "is_verified": False,
        },
        {
            "username": "moderator",
            "email": "mod@demo.com",
            "password": "Mod@Demo123!",
            "first_name": "Mod",
            "last_name": "User",
            "role": RoleEnum.MODERATOR.value,
            "is_verified": True,
        },
    ]

    with app.app_context():
        for u in demo_users:
            if not User.query.filter_by(email=u["email"]).first():
                hashed = bcrypt.generate_password_hash(
                    u["password"], rounds=app.config["BCRYPT_LOG_ROUNDS"]
                ).decode("utf-8")
                user = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hashed,
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    role=u["role"],
                    is_active=True,
                    is_verified=u["is_verified"],
                )
                db.session.add(user)
                print(f"  ✓ Seeded user: {u['email']} (password: {u['password']})")
        db.session.commit()
        print("\nDemo seed complete.")


if __name__ == "__main__":
    app = create_app("development")
    print("\nSeeding demo users…")
    seed_demo_users(app)
    print("\nCredentials:")
    print("  Admin     → admin@securehub.io  / Admin@SecureHub123!")
    print("  Alice     → alice@demo.com       / Alice@Demo123!")
    print("  Bob       → bob@demo.com         / Bob@Demo123!")
    print("  Moderator → mod@demo.com         / Mod@Demo123!")
