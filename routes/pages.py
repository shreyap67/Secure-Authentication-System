"""
routes/pages.py — Server-rendered page routes
"""

from flask import Blueprint, render_template, redirect, url_for

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def landing():       return render_template("landing.html")

@pages_bp.get("/register")
def register():      return render_template("register.html")

@pages_bp.get("/login")
def login():         return render_template("login.html")

@pages_bp.get("/login/2fa")
def login_2fa():     return render_template("login_2fa.html")

@pages_bp.get("/dashboard")
def dashboard():     return render_template("dashboard.html")

@pages_bp.get("/admin")
def admin_dashboard(): return render_template("admin_dashboard.html")

@pages_bp.get("/admin/analytics")
def admin_analytics(): return render_template("admin_analytics.html")

@pages_bp.get("/profile")
def profile():       return render_template("profile.html")

@pages_bp.get("/forgot-password")
def forgot_password(): return render_template("forgot_password.html")

@pages_bp.get("/reset-password")
def reset_password(): return render_template("reset_password.html")

@pages_bp.get("/access-denied")
def access_denied(): return render_template("access_denied.html"), 403

@pages_bp.app_errorhandler(404)
def not_found(e):    return render_template("404.html"), 404

@pages_bp.app_errorhandler(500)
def server_error(e): return render_template("500.html"), 500
