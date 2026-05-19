# 🔐 SecureHub — Secure Authentication & User Management Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**A production-grade authentication and user management platform built with Flask, PostgreSQL, JWT, and bcrypt — designed to demonstrate enterprise security practices.**

[Features](#-features) · [Tech Stack](#-tech-stack) · [Quick Start](#-quick-start) · [API Docs](#-api-endpoints) · [Deployment](#-deployment) · [Security](#-security-architecture)

</div>

---

## 📋 Project Overview

SecureHub is an **industrial-grade authentication backend** simulating real-world enterprise security infrastructure. It implements the full authentication lifecycle — from registration to session invalidation — using modern security standards and clean modular architecture.

> **Portfolio Highlight:** This project demonstrates mastery of JWT authentication, cryptographic password hashing, role-based access control, input sanitization, rate limiting, audit logging, and clean Flask application architecture — skills directly applicable to backend engineering roles.

---

## ✨ Features

### 🔑 Authentication
- **JWT Access + Refresh Token** flow with configurable expiry
- **Bcrypt password hashing** with configurable cost factor (never plain-text)
- **Token blacklisting** on logout (persisted to database)
- **Automatic token refresh** via refresh token endpoint
- **Secure cookie + Authorization header** token delivery

### 🛡️ Security
- **Brute-force protection** — account lockout after N failed attempts
- **Rate limiting** — per-IP limits on login and registration endpoints
- **Input sanitization** — bleach-based XSS prevention on all user inputs
- **SQL injection prevention** — SQLAlchemy ORM, no raw queries
- **Security headers** — CSP, HSTS, X-Frame-Options, X-XSS-Protection
- **CSRF protection** — Flask-WTF CSRF tokens on form submissions
- **Password strength enforcement** — uppercase, lowercase, digit, special char required

### 👥 Role-Based Access Control
| Role      | Capabilities                                              |
|-----------|-----------------------------------------------------------|
| Admin     | Full user management, audit logs, stats, delete users     |
| Moderator | Elevated content access, moderation tools                 |
| User      | Profile management, password change, session management   |

### 📊 User Management
- User registration with email validation and duplicate prevention
- Profile update (name, bio, avatar URL)
- Password change with current-password verification
- Email verification flow with secure token
- Forgot password / reset password with expiring token

### 📝 Audit Logging
Every authentication event is logged with:
- User ID, Action, Resource, Status
- IP Address, User-Agent
- Timestamp (UTC)

### 🏗️ Architecture
- **Flask Blueprints** for modular route separation
- **Service layer** isolating business logic from HTTP concerns
- **Middleware layer** for JWT callbacks and security headers
- **Repository pattern** via SQLAlchemy ORM
- **Environment-based config** (development / production / testing)

---

## 🛠️ Tech Stack

| Layer          | Technology                        |
|----------------|-----------------------------------|
| Language       | Python 3.12                       |
| Framework      | Flask 3.0                         |
| Database       | PostgreSQL 16                     |
| ORM            | SQLAlchemy 2.0 + Flask-Migrate    |
| Authentication | Flask-JWT-Extended (PyJWT)        |
| Password Hash  | bcrypt via Flask-Bcrypt           |
| Rate Limiting  | Flask-Limiter                     |
| Input Safety   | bleach, email-validator           |
| CORS           | Flask-CORS                        |
| Frontend       | Jinja2 templates, vanilla JS      |
| Container      | Docker + Docker Compose           |
| Production     | Gunicorn WSGI server              |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

### 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/Secure-Authentication-System.git
cd Secure-Authentication-System
```

### 2 — Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows
```

### 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/secure_auth_db
ADMIN_EMAIL=admin@securehub.io
ADMIN_PASSWORD=Admin@SecureHub123!
```

### 5 — Create the PostgreSQL Database

```bash
psql -U postgres -c "CREATE DATABASE secure_auth_db;"
```

### 6 — Run Database Migrations

```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

### 7 — Start the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

**Default admin credentials:**
```
Email:    admin@securehub.io
Password: Admin@SecureHub123!
```

---

## 🐳 Docker Quickstart

```bash
# Start app + PostgreSQL + Redis
docker compose up --build

# First run auto-creates the database, runs migrations, and seeds the admin account
```

Visit: **http://localhost:5000**

---

## 📁 Project Structure

```
Secure-Authentication-System/
│
├── app.py                    ← Application factory & entry point
├── config.py                 ← Environment-based configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml               ← Render.com deployment config
├── Procfile                  ← Heroku/Railway deployment
├── .env.example
│
├── database/
│   ├── __init__.py           ← SQLAlchemy, Migrate, bcrypt instances
│   ├── schema.sql            ← Reference SQL schema
│   └── seed.py               ← Demo data seeder
│
├── models/
│   ├── __init__.py
│   └── user.py               ← User, Role, UserSession, TokenBlacklist, AuditLog
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
│   └── user_service.py       ← Profile, admin management logic
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
│   ├── base.html             ← Base template (fonts, CSS, toast container)
│   ├── landing.html          ← Public landing page
│   ├── login.html            ← Login form
│   ├── register.html         ← Registration form
│   ├── dashboard.html        ← User dashboard
│   ├── admin_dashboard.html  ← Admin panel
│   ├── profile.html          ← Profile + password settings
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
├── migrations/               ← Alembic auto-migration files
└── logs/                     ← Rotating log files (auto-created)
```

---

## 🌐 API Endpoints

### Authentication — `/api/auth`

| Method | Endpoint                     | Auth | Description                          |
|--------|------------------------------|------|--------------------------------------|
| POST   | `/api/auth/register`         | No   | Create new user account              |
| POST   | `/api/auth/login`            | No   | Authenticate and receive JWT tokens  |
| POST   | `/api/auth/logout`           | Yes  | Blacklist current access token       |
| POST   | `/api/auth/refresh`          | Yes* | Issue new access token via refresh   |
| GET    | `/api/auth/me`               | Yes  | Get authenticated user profile       |
| GET    | `/api/auth/verify-email/<t>` | No   | Verify email with token              |
| POST   | `/api/auth/forgot-password`  | No   | Request password reset email         |
| POST   | `/api/auth/reset-password`   | No   | Submit new password with reset token |

### User Profile — `/api/user`

| Method | Endpoint                   | Auth | Description               |
|--------|----------------------------|------|---------------------------|
| GET    | `/api/user/profile`        | Yes  | Get own profile           |
| PUT    | `/api/user/profile`        | Yes  | Update profile fields     |
| POST   | `/api/user/change-password`| Yes  | Change password           |
| GET    | `/api/user/sessions`       | Yes  | List active sessions      |
| GET    | `/api/user/audit-logs`     | Yes  | Get own audit log history |

### Admin — `/api/admin`

| Method | Endpoint                   | Admin | Description                  |
|--------|----------------------------|-------|------------------------------|
| GET    | `/api/admin/users`         | Yes   | List all users (paginated)   |
| GET    | `/api/admin/users/<id>`    | Yes   | Get single user              |
| PUT    | `/api/admin/users/<id>`    | Yes   | Update user role/status      |
| DELETE | `/api/admin/users/<id>`    | Yes   | Delete user account          |
| GET    | `/api/admin/stats`         | Yes   | Platform statistics          |
| GET    | `/api/admin/audit-logs`    | Yes   | All audit logs (paginated)   |

### Health
| Method | Endpoint       | Description   |
|--------|----------------|---------------|
| GET    | `/api/health`  | Health check  |

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
  "user": { "id": 2, "username": "janedoe", "role": "user", ... }
}
```

**Authorization Header (all protected routes)**
```
Authorization: Bearer <access_token>
```

---

## 🔐 Security Architecture

### Authentication Flow

```
Client                          Server
  │                               │
  ├─POST /api/auth/login─────────►│
  │   {identifier, password}      │  1. Find user by email/username
  │                               │  2. Check account lock status
  │                               │  3. bcrypt.check_password_hash()
  │                               │  4. Reset failed_login_attempts
  │                               │  5. Create JWT (access + refresh)
  │                               │  6. Write audit log
  │◄──{access_token, refresh}─────│
  │                               │
  ├─GET /api/user/profile────────►│
  │   Authorization: Bearer ...   │  1. Decode JWT header
  │                               │  2. Check TokenBlacklist (jti)
  │                               │  3. Validate expiry
  │                               │  4. Load user from claims
  │◄──{user profile}──────────────│
  │                               │
  ├─POST /api/auth/logout────────►│
  │   Authorization: Bearer ...   │  1. Extract jti from JWT
  │                               │  2. INSERT INTO token_blacklist
  │◄──{success: true}─────────────│
  │                               │
  ├─POST /api/auth/refresh───────►│ (using refresh token)
  │   Authorization: Bearer ...   │  1. Validate refresh token
  │                               │  2. Issue new access token
  │◄──{access_token}──────────────│
```

### Password Security
- **bcrypt** with configurable work factor (default: 12 rounds)
- Each password gets a unique **random salt** automatically
- **Minimum requirements**: 8+ chars, uppercase, lowercase, digit, special character
- Common password blacklist check
- Current password verification required for password changes

### Brute-Force Protection
```
Login attempt → increment failed_login_attempts
If attempts >= MAX_LOGIN_ATTEMPTS (default: 5):
    SET locked_until = NOW() + LOCKOUT_DURATION (default: 15 min)
On successful login:
    RESET failed_login_attempts = 0, locked_until = NULL
```

### JWT Security
- **Short-lived access tokens** (15 minutes default)
- **Long-lived refresh tokens** (7 days default) stored securely
- **jti (JWT ID)** uniquely identifies each token
- **TokenBlacklist table** prevents use of revoked tokens
- Role and email embedded in JWT claims for fast authorization

---

## 🚀 Deployment

### Render.com (Recommended)

1. Push to GitHub
2. Connect repo on [render.com](https://render.com)
3. Select **Web Service** → **Python**
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app --workers 4 --bind 0.0.0.0:$PORT`
6. Add environment variables from `.env.example`
7. Add a **PostgreSQL** database and link `DATABASE_URL`

Or use the included `render.yaml`:
```bash
# Push render.yaml to your repo — Render auto-detects it
```

### Railway

```bash
railway login
railway init
railway add postgresql
railway up
```

### Heroku

```bash
heroku create securehub-app
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
git push heroku main
heroku run flask db upgrade
```

### Docker (Self-hosted)

```bash
docker compose up --build -d
docker compose exec app flask db upgrade
```

---

## 🧪 Testing the API

Using **curl**:

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test@1234!"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com","password":"Test@1234!"}'

# Access protected route
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <your_access_token>"

# Admin: list users
curl http://localhost:5000/api/admin/users \
  -H "Authorization: Bearer <admin_access_token>"
```

---

## 🌱 Seeding Demo Data

```bash
python database/seed.py
```

Creates demo accounts:

| Email              | Password          | Role      |
|--------------------|-------------------|-----------|
| admin@securehub.io | Admin@SecureHub123! | Admin   |
| alice@demo.com     | Alice@Demo123!    | User      |
| bob@demo.com       | Bob@Demo123!      | User      |
| mod@demo.com       | Mod@Demo123!      | Moderator |

---

## 📄 Environment Variables Reference

| Variable              | Description                        | Default               |
|-----------------------|------------------------------------|-----------------------|
| `SECRET_KEY`          | Flask session secret               | *(required)*          |
| `JWT_SECRET_KEY`      | JWT signing secret                 | *(required)*          |
| `DATABASE_URL`        | PostgreSQL connection string       | *(required)*          |
| `FLASK_ENV`           | `development` / `production`       | `development`         |
| `BCRYPT_LOG_ROUNDS`   | bcrypt cost factor                 | `12`                  |
| `MAX_LOGIN_ATTEMPTS`  | Lockout threshold                  | `5`                   |
| `LOCKOUT_DURATION`    | Lockout seconds                    | `900` (15 min)        |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token TTL seconds      | `900` (15 min)        |
| `JWT_REFRESH_TOKEN_EXPIRES`| Refresh token TTL seconds     | `604800` (7 days)     |
| `ADMIN_EMAIL`         | Seeded admin email                 | `admin@securehub.io`  |
| `ADMIN_PASSWORD`      | Seeded admin password              | *(set in .env)*       |

---

## 🧠 Interview Explanation

> **"Tell me about this project."**

SecureHub is a production-ready authentication backend I built to demonstrate enterprise security patterns. At its core, it implements JWT-based stateless authentication with access and refresh tokens — access tokens expire in 15 minutes to limit exposure, while refresh tokens allow seamless session persistence.

For password security, I use bcrypt with a work factor of 12, which means each hash takes roughly 250ms — too slow for brute-force attacks at scale. Passwords are never stored in plain text, and each one gets a unique random salt automatically through bcrypt's design.

I implemented role-based access control using custom Flask decorators that verify JWT claims — `@admin_required` extracts the role from the token payload and returns 403 before the route handler even executes. Token revocation is handled via a `token_blacklist` table keyed on the JWT's `jti` (unique ID), which gets checked on every request.

For defense-in-depth, I added brute-force protection (account lockout after 5 failed attempts), per-IP rate limiting on auth endpoints, input sanitization with bleach, and security headers including CSP and HSTS. Every authentication event writes to an audit log with IP, user agent, and outcome.

The architecture follows Flask Blueprints for route separation, a service layer to keep business logic out of route handlers, and environment-based configuration for clean dev/prod switching.

---

## 📜 Resume Description

**Secure Authentication & User Management Platform** | Python, Flask, PostgreSQL, JWT

> Built a production-grade authentication backend with JWT access/refresh token flow, bcrypt password hashing (cost factor 12), and token blacklisting for secure logout. Implemented role-based access control (Admin/User/Moderator) using custom Flask middleware decorators. Added enterprise security features: account lockout after failed attempts, per-IP rate limiting, input sanitization (XSS prevention), SQL injection protection via SQLAlchemy ORM, and CSP/HSTS security headers. Designed modular architecture with Flask Blueprints, service layer, and full audit logging. Containerized with Docker and deployed on Render with PostgreSQL.

---

## 📃 License

MIT — free to use, modify, and distribute for personal and commercial projects.

---

<div align="center">
Built with 🔐 by SecureHub · Enterprise Authentication Done Right
</div>
"# Secure-Authentication-System" 
