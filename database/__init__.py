"""
database/__init__.py — SQLAlchemy & Migration instances
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def init_db(app):
    """Bind database extensions to the Flask application."""
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
