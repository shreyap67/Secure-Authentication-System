"""
utils/__init__.py — Logging configuration
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configure structured logging with rotation."""
    log_level = logging.DEBUG if app.debug else logging.INFO

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s (%(funcName)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # File handler
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10_000_000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(log_level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    app.logger.setLevel(log_level)
    app.logger.info("Logging initialized.")
