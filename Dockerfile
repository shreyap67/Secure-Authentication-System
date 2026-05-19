# ================================================================
# SecureHub — Dockerfile
# ================================================================
# Build:   docker build -t securehub .
# Run:     docker run -p 5000:5000 --env-file .env securehub
# ================================================================

FROM python:3.12-slim

# Metadata
LABEL maintainer="SecureHub Team"
LABEL description="Secure Authentication & User Management Platform"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create non-root user (security best practice)
RUN addgroup --system securehub && adduser --system --ingroup securehub securehub
RUN chown -R securehub:securehub /app
USER securehub

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Production: run with Gunicorn (multi-worker WSGI server)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]
