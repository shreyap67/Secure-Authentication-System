-- ================================================================
-- SecureHub — PostgreSQL Schema Reference
-- ================================================================
-- This file documents the schema created by SQLAlchemy migrations.
-- Run migrations instead of this file directly:
--   flask db upgrade
-- ================================================================

-- Create Database
CREATE DATABASE secure_auth_db;
\c secure_auth_db;

-- ── Roles ─────────────────────────────────────────────────────────
CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)  UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── Users ─────────────────────────────────────────────────────────
CREATE TABLE users (
    id                      SERIAL PRIMARY KEY,
    username                VARCHAR(80)  UNIQUE NOT NULL,
    email                   VARCHAR(255) UNIQUE NOT NULL,
    hashed_password         VARCHAR(255) NOT NULL,

    -- Profile
    first_name              VARCHAR(100),
    last_name               VARCHAR(100),
    avatar_url              VARCHAR(512),
    bio                     TEXT,

    -- Primary role shortcut
    role                    VARCHAR(20)  NOT NULL DEFAULT 'user',

    -- Account state
    is_active               BOOLEAN      NOT NULL DEFAULT TRUE,
    is_verified             BOOLEAN      NOT NULL DEFAULT FALSE,
    email_verified_at       TIMESTAMPTZ,
    verification_token      VARCHAR(255),

    -- Security / brute-force protection
    failed_login_attempts   INT          NOT NULL DEFAULT 0,
    locked_until            TIMESTAMPTZ,
    last_login_at           TIMESTAMPTZ,
    last_login_ip           VARCHAR(45),
    password_changed_at     TIMESTAMPTZ,
    reset_password_token    VARCHAR(255),
    reset_password_expires  TIMESTAMPTZ,

    -- Timestamps
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ           DEFAULT NOW()
);

CREATE INDEX idx_users_email    ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ── User ↔ Role (many-to-many) ────────────────────────────────────
CREATE TABLE user_roles (
    user_id  INT REFERENCES users(id) ON DELETE CASCADE,
    role_id  INT REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- ── User Sessions ─────────────────────────────────────────────────
CREATE TABLE user_sessions (
    id            SERIAL PRIMARY KEY,
    user_id       INT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(512) UNIQUE NOT NULL,
    ip_address    VARCHAR(45),
    user_agent    VARCHAR(512),
    device_info   VARCHAR(255),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at    TIMESTAMPTZ,
    last_activity TIMESTAMPTZ           DEFAULT NOW()
);

CREATE INDEX idx_sessions_token   ON user_sessions(session_token);
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);

-- ── Token Blacklist ───────────────────────────────────────────────
CREATE TABLE token_blacklist (
    id          SERIAL PRIMARY KEY,
    jti         VARCHAR(36)  UNIQUE NOT NULL,
    token_type  VARCHAR(20)  NOT NULL,
    user_id     INT          REFERENCES users(id) ON DELETE CASCADE,
    revoked_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ
);

CREATE INDEX idx_blacklist_jti ON token_blacklist(jti);

-- ── Audit Logs ────────────────────────────────────────────────────
CREATE TABLE audit_logs (
    id          SERIAL PRIMARY KEY,
    user_id     INT          REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(100),
    resource_id VARCHAR(50),
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(512),
    status      VARCHAR(20)  NOT NULL DEFAULT 'success',
    details     TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id   ON audit_logs(user_id);
CREATE INDEX idx_audit_action    ON audit_logs(action);
CREATE INDEX idx_audit_created   ON audit_logs(created_at DESC);

-- ── Seed Default Roles ────────────────────────────────────────────
INSERT INTO roles (name, description) VALUES
    ('admin',     'Full platform access'),
    ('user',      'Standard user access'),
    ('moderator', 'Elevated content permissions');
