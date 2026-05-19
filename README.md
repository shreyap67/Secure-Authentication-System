# 🔐 SecureHub — Enterprise Authentication & User Management Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Default-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Optional-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![2FA](https://img.shields.io/badge/2FA-TOTP-green?style=for-the-badge&logo=authy&logoColor=white)

**A production-grade authentication and user management platform built with Flask, SQLAlchemy, JWT, and bcrypt — designed to demonstrate enterprise security practices.**

[Features](#-features) · [Tech Stack](#-tech-stack) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Deployment](#-deployment) · [Security](#-security-architecture)

</div>

---

## 📋 Overview

SecureHub is a **full-stack authentication backend** that simulates real-world enterprise security infrastructure. It implements the complete authentication lifecycle — from registration through session invalidation — using modern security standards and clean modular architecture.

**Zero-setup by default:** uses SQLite out of the box with no database installation required. Seamlessly upgrades to PostgreSQL by setting a single environment variable.

> **Portfolio Highlight:** Demonstrates mastery of JWT authentication, TOTP two-factor auth, bcrypt password hashing, role-based access control, input sanitization, rate limiting, audit logging, login history tracking, and clean Flask Blueprint architecture.

---

## ✨ Features

### 🔑 Authentication
- **JWT Access + Refresh Token** flow with configurable expiry (15 min / 7 days)
- **Bcrypt password hashing** with configurable cost factor — never plain-text
- **Token blacklisting** on logout, persisted to the database via `jti`
- **Automatic token refresh** endpoint using the long-lived refresh token
- **Dual token delivery** — secure cookies and `Authorization: Bearer` header

### 🔒 Two-Factor Authentication (TOTP)
- **TOTP-based 2FA** powered by `pyotp` — compatible with Google Authenticator, Authy, and any RFC 6238 app
- **QR code generation** rendered as base64 PNG for seamless setup UI
- **Backup recovery codes** generated on 2FA enrollment
- **Per-user enable / disable** flow with verification before activation

### 🛡️ Security
- **Brute-force protection** — account lockout after N failed attempts (configurable)
- **Per-IP rate limiting** on login and registration endpoints via Flask-Limiter
- **Input sanitization** — `bleach`-based XSS prevention on all user inputs
- **SQL injection prevention** — SQLAlchemy ORM, zero raw queries
- **Security headers** — CSP, HSTS, X-Frame-Options, X-Content-Type, X-XSS-Protection
- **CSRF protection** — Flask-WTF CSRF tokens on all form submissions
- **Password strength enforcement** — uppercase, lowercase, digit, and special character required

### 👥 Role-Based Access Control

| Role      | Capabilities                                                  |
|-----------|---------------------------------------------------------------|
| Admin     | Full user management, audit logs, analytics, delete accounts  |
| Moderator | Elevated access, moderation tools                             |
| User      | Profile management, password change, session management       |

### 📊 User Management
- Registration with email validation and duplicate prevention
- Profile update (first name, last name, bio, avatar URL)
- Secure password change with current-password verification
- Email verification flow with expiring cryptographic token
- Forgot password / reset password with time-limited token
- OAuth-ready architecture (Google sign-in scaffold included)

### 📈 Analytics & Audit
- **Admin analytics dashboard** with Plotly-powered charts
- **Login history tracking** — IP address, user agent, timestamp, success/failure per attempt
- **Full audit log** — every authentication event recorded with user ID, action, resource, status, IP, and UTC timestamp
- Paginated audit log views for both users (own history) and admins (all users)

### 🏗️ Architecture
- **Flask Blueprints** — clean separation of `auth`, `user`, `admin`, and `pages` routes
- **Service layer** — business logic fully decoupled from HTTP handlers
- **Middleware layer** — JWT callbacks and security header injection
- **Environment-based config** — `development`, `production`, and `testing` profiles
- **Swagger / OpenAPI** — interactive API docs auto-generated at `/api/docs`

---

## 🛠️ Tech Stack

| Layer          | Technology                                  |
|----------------|---------------------------------------------|
| Language       | Python 3.12                                 |
| Framework      | Flask 3.0                                   |
| Database       | SQLite (default) · PostgreSQL (optional)    |
| ORM            | SQLAlchemy 2.0 + Flask-Migrate (Alembic)    |
| Authentication | Flask-JWT-Extended (PyJWT)                  |
| 2FA            | pyotp (TOTP) + qrcode + Pillow              |
| Password Hash  | bcrypt via Flask-Bcrypt                     |
| Rate Limiting  | Flask-Limiter (memory or Redis backend)     |
| Input Safety   | bleach, email-validator                     |
| Mail           | Flask-Mail (SMTP)                           |
| CORS           | Flask-CORS                                  |
| API Docs       | Flasgger (Swagger UI)                       |
| Analytics      | Plotly                                      |
| Frontend       | Jinja2 templates + vanilla JS               |
| Container      | Docker + Docker Compose                     |
| Production     | Gunicorn WSGI server                        |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git

> **No database installation needed** — SQLite runs out of the box.

---

### 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/SecureHub.git
cd SecureHub
```

### 2 — Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Optional: leave blank to use SQLite (default)
# DATABASE_URL=postgresql://postgres:password@localhost:5432/securehub_db

ADMIN_EMAIL=admin@securehub.io
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@SecureHub123!

# Optional: email (for verification & password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5 — Start the Application

```bash
python app.py
```

The app automatically creates the SQLite database, runs all table migrations, and seeds the admin account on first launch.

Visit: **http://localhost:5000**

**Default admin credentials:**
```
Email:    admin@securehub.io
Password: Admin@SecureHub123!
```

**Swagger API Docs:** http://localhost:5000/api/docs

---

## 🐳 Docker Quickstart

```bash
# Build and start the application
docker compose up --build

# The database is created and seeded automatically on first run
```

Visit: **http://localhost:5000**

---

## 🗄️ Using PostgreSQL (Optional)

SQLite is the default and requires no setup. To switch to PostgreSQL:

1. Create a PostgreSQL database:
   ```bash
   psql -U postgres -c "CREATE DATABASE securehub_db;"
   ```

2. Set `DATABASE_URL` in your `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/securehub_db
   ```

3. Restart the application — Flask-Migrate handles the schema automatically.

---

## 📁 Project Structure

```
SecureHub/
│
├── app.py                    ← Application factory & entry point
├── config.py                 ← Environment-based configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml               ← Render.com deployment config
├── Procfile                  ← Heroku / Railway deployment
├── .env.example
│
├── database/
│   ├── __init__.py           ← SQLAlchemy, Migrate, bcrypt instances
│   ├── schema.sql            ← Reference SQL schema
│   └── seed.py               ← Demo data seeder
│
├── models/
│   ├── __init__.py
│   └── user.py               ← User, Role, UserSession, TokenBlacklist,
│                               AuditLog, LoginHistory models
│
├── routes/
│   ├── __init__.py
│   ├── auth.py               ← /api/auth/* endpoints
│   ├── user.py               ← /api/user/* endpoints
│   ├── admin.py              ← /api/admin/* endpoints
│   └── pages.py              ← HTML page routes
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py       ← Registration, login, logout, reset logic
│   ├── twofa_service.py      ← TOTP 2FA setup, verification, backup codes
│   └── user_service.py       ← Profile update, admin management logic
│
├── middleware/
│   ├── __init__.py           ← JWT callbacks, security headers
│   └── decorators.py         ← @admin_required, @roles_required, @active_user_required
│
├── utils/
│   ├── __init__.py           ← Logging setup
│   └── validators.py         ← Password strength, email, username validation
│
├── templates/
│   ├── base.html             ← Base layout (fonts, CSS, toast container)
│   ├── landing.html          ← Public landing page
│   ├── login.html            ← Login form
│   ├── login_2fa.html        ← TOTP verification step
│   ├── register.html         ← Registration form
│   ├── dashboard.html        ← User dashboard
│   ├── admin_dashboard.html  ← Admin panel
│   ├── admin_analytics.html  ← Plotly analytics dashboard
│   ├── profile.html          ← Profile & 2FA settings
│   ├── forgot_password.html  ← Forgot password form
│   ├── reset_password.html   ← Password reset form
│   ├── access_denied.html    ← 403 page
│   ├── 404.html
│   └── 500.html
│
├── static/
│   ├── css/main.css          ← Full design system (dark, glassmorphism)
│   └── js/app.js             ← API client, auth state, toast, form helpers
│
└── migrations/               ← Alembic auto-migration files
```

---

## 🌐 API Reference

### Authentication — `/api/auth`

| Method | Endpoint                     | Auth Required | Description                          |
|--------|------------------------------|:---:|--------------------------------------|
| POST   | `/api/auth/register`         | No  | Create a new user account            |
| POST   | `/api/auth/login`            | No  | Authenticate and receive JWT tokens  |
| POST   | `/api/auth/logout`           | Yes | Blacklist current access token       |
| POST   | `/api/auth/refresh`          | Yes*| Issue new access token via refresh   |
| GET    | `/api/auth/me`               | Yes | Get authenticated user profile       |
| GET    | `/api/auth/verify-email/<t>` | No  | Verify email address with token      |
| POST   | `/api/auth/forgot-password`  | No  | Request a password reset email       |
| POST   | `/api/auth/reset-password`   | No  | Submit new password with reset token |

### User Profile — `/api/user`

| Method | Endpoint                      | Auth Required | Description                    |
|--------|-------------------------------|:---:|--------------------------------|
| GET    | `/api/user/profile`           | Yes | Retrieve own profile           |
| PUT    | `/api/user/profile`           | Yes | Update profile fields          |
| POST   | `/api/user/change-password`   | Yes | Change password (verified)     |
| GET    | `/api/user/sessions`          | Yes | List active sessions           |
| GET    | `/api/user/audit-logs`        | Yes | Retrieve own audit log history |
| POST   | `/api/user/2fa/setup`         | Yes | Generate TOTP secret + QR code |
| POST   | `/api/user/2fa/enable`        | Yes | Confirm and enable 2FA         |
| POST   | `/api/user/2fa/disable`       | Yes | Disable 2FA (password verified)|

### Admin — `/api/admin`

| Method | Endpoint                   | Admin Only | Description                    |
|--------|----------------------------|:---:|--------------------------------|
| GET    | `/api/admin/users`         | Yes | List all users (paginated)     |
| GET    | `/api/admin/users/<id>`    | Yes | Get a single user              |
| PUT    | `/api/admin/users/<id>`    | Yes | Update user role or status     |
| DELETE | `/api/admin/users/<id>`    | Yes | Delete a user account          |
| GET    | `/api/admin/stats`         | Yes | Platform-wide statistics       |
| GET    | `/api/admin/audit-logs`    | Yes | All audit logs (paginated)     |

### Health

| Method | Endpoint      | Description         |
|--------|---------------|---------------------|
| GET    | `/api/health` | Service health check|

---

### Request / Response Examples

**POST `/api/auth/register`**
```json
// Request
{
  "username": "janedoe",
  "email": "jane@example.com",
  "password": "Jane@Secure123!",
  "first_name": "Jane",
  "last_name": "Doe"
}

// Response 201
{
  "success": true,
  "message": "Account created successfully.",
  "user": {
    "id": 2,
    "username": "janedoe",
    "email": "jane@example.com",
    "role": "user",
    "is_verified": false,
    "created_at": "2025-01-15T10:30:00+00:00"
  }
}
```

**POST `/api/auth/login`**
```json
// Request
{
  "identifier": "jane@example.com",
  "password": "Jane@Secure123!"
}

// Response 200
{
  "success": true,
  "message": "Login successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { "id": 2, "username": "janedoe", "role": "user" }
}
```

**Authorization header (all protected routes)**
```
Authorization: Bearer <access_token>
```

---

## 🔐 Security Architecture

### Authentication Flow

```
Client                              Server
  │                                   │
  ├─ POST /api/auth/login ───────────►│
  │   {identifier, password}          │  1. Lookup user by email or username
  │                                   │  2. Check account lock status
  │                                   │  3. bcrypt.check_password_hash()
  │                                   │  4. Reset failed_login_attempts
  │                                   │  5. Issue JWT access + refresh tokens
  │                                   │  6. Record login history entry
  │                                   │  7. Write audit log
  │◄─ {access_token, refresh_token} ──│
  │                                   │
  ├─ GET /api/user/profile ──────────►│
  │   Authorization: Bearer ...       │  1. Decode JWT from header / cookie
  │                                   │  2. Check TokenBlacklist by jti
  │                                   │  3. Validate expiry
  │                                   │  4. Load user from JWT claims
  │◄─ {user profile} ─────────────────│
  │                                   │
  ├─ POST /api/auth/logout ──────────►│
  │   Authorization: Bearer ...       │  1. Extract jti from JWT
  │                                   │  2. INSERT INTO token_blacklist
  │◄─ {success: true} ────────────────│
  │                                   │
  ├─ POST /api/auth/refresh ─────────►│  (using refresh token)
  │   Authorization: Bearer ...       │  1. Validate refresh token
  │                                   │  2. Issue new access token
  │◄─ {access_token} ─────────────────│
```

### TOTP Two-Factor Flow

```
  ├─ POST /api/user/2fa/setup ───────►│  1. Generate random TOTP secret
  │                                   │  2. Build otpauth:// URI
  │                                   │  3. Render QR code as base64 PNG
  │◄─ {secret, qr_code_base64} ───────│
  │  (user scans QR in authenticator) │
  │                                   │
  ├─ POST /api/user/2fa/enable ──────►│  1. Verify submitted TOTP code
  │   {totp_code}                     │  2. Enable 2FA on account
  │                                   │  3. Generate backup recovery codes
  │◄─ {backup_codes} ─────────────────│
```

### Password Security

- **bcrypt** with configurable work factor (default: 12 rounds ≈ 250ms per hash)
- Each password receives a unique **random salt** via bcrypt's built-in design
- **Minimum requirements:** 8+ characters, uppercase, lowercase, digit, special character
- Current-password verification required for all password changes

### Brute-Force Protection

```
Login attempt → increment failed_login_attempts
If attempts >= MAX_LOGIN_ATTEMPTS (default 5):
    SET locked_until = NOW() + LOCKOUT_DURATION (default 15 min)
On successful login:
    RESET failed_login_attempts = 0
    RESET locked_until = NULL
```

### JWT Security

- **Short-lived access tokens** — 15 minutes by default
- **Long-lived refresh tokens** — 7 days by default
- **jti (JWT ID)** uniquely identifies every issued token
- **TokenBlacklist table** checked on every authenticated request to enforce logout

---

## 🚀 Deployment

### Render.com (Recommended)

1. Push the repository to GitHub
2. Connect the repo at [render.com](https://render.com)
3. Select **Web Service → Python**
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app --workers 4 --bind 0.0.0.0:$PORT`
6. Add environment variables from `.env.example`

Or use the included `render.yaml` — Render auto-detects it on push.

### Railway

```bash
railway login
railway init
railway up
```

### Heroku

```bash
heroku create securehub-app
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
git push heroku main
```

### Docker (Self-Hosted)

```bash
docker compose up --build -d
```

---

## 🧪 Testing the API

**Using curl:**

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test@1234!","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com","password":"Test@1234!"}'

# Access protected route
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <your_access_token>"

# Admin: list all users
curl http://localhost:5000/api/admin/users \
  -H "Authorization: Bearer <admin_access_token>"

# Health check
curl http://localhost:5000/api/health
```

Or use the interactive **Swagger UI** at `http://localhost:5000/api/docs`.

---

## 🌱 Seeding Demo Data

```bash
python database/seed.py
```

Creates the following demo accounts:

| Email               | Password            | Role      |
|---------------------|---------------------|-----------|
| admin@securehub.io  | Admin@SecureHub123! | Admin     |
| alice@demo.com      | Alice@Demo123!      | User      |
| bob@demo.com        | Bob@Demo123!        | User      |
| mod@demo.com        | Mod@Demo123!        | Moderator |

---

## ⚙️ Environment Variables Reference

| Variable                    | Description                              | Default               |
|-----------------------------|------------------------------------------|-----------------------|
| `SECRET_KEY`                | Flask session secret                     | *(required)*          |
| `JWT_SECRET_KEY`            | JWT signing secret                       | *(required)*          |
| `DATABASE_URL`              | DB connection string (omit for SQLite)   | `sqlite:///securehub.db` |
| `FLASK_ENV`                 | `development` / `production`             | `development`         |
| `BCRYPT_LOG_ROUNDS`         | bcrypt cost factor                       | `12`                  |
| `MAX_LOGIN_ATTEMPTS`        | Failed attempts before lockout           | `5`                   |
| `LOCKOUT_DURATION`          | Lockout duration in seconds              | `900` (15 min)        |
| `JWT_ACCESS_TOKEN_EXPIRES`  | Access token TTL in seconds              | `900` (15 min)        |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh token TTL in seconds             | `604800` (7 days)     |
| `RATELIMIT_DEFAULT`         | Flask-Limiter default rule               | `200/day;50/hour`     |
| `REDIS_URL`                 | Redis URL for rate limiting (optional)   | `memory://`           |
| `MAIL_SERVER`               | SMTP server                              | `smtp.gmail.com`      |
| `MAIL_PORT`                 | SMTP port                                | `587`                 |
| `MAIL_USERNAME`             | SMTP username / email                    | —                     |
| `MAIL_PASSWORD`             | SMTP password / app password             | —                     |
| `ADMIN_EMAIL`               | Seeded admin email                       | `admin@securehub.io`  |
| `ADMIN_USERNAME`            | Seeded admin username                    | `admin`               |
| `ADMIN_PASSWORD`            | Seeded admin password                    | *(set in .env)*       |

---

## 📜 Resume Description

**Secure Authentication & User Management Platform** | Python · Flask · SQLite/PostgreSQL · JWT · TOTP

> Built a production-grade authentication backend featuring JWT access/refresh token flow, TOTP two-factor authentication with QR code provisioning, and bcrypt password hashing (cost factor 12). Implemented role-based access control (Admin/Moderator/User) via custom Flask middleware decorators. Enterprise security features include: account lockout after failed attempts, per-IP rate limiting, bleach-based XSS sanitization, SQLAlchemy ORM for SQL injection prevention, and CSP/HSTS security headers. Added full audit logging, login history tracking, and a Plotly-powered admin analytics dashboard. Zero-setup SQLite default with seamless PostgreSQL upgrade path. Containerized with Docker and deployable to Render, Railway, or Heroku.

---

## 📃 License

MIT — free to use, modify, and distribute for personal and commercial projects.

---

<div align="center">
Built with 🔐 by SecureHub · Enterprise Authentication Done Right
</div>
