# syntax=docker/dockerfile:1

# ==============================================================================
# Stage 1: Build stage using uv for locked dependency resolution and installation
# ==============================================================================
FROM python:3.14-slim AS builder

# Copy official uv binary from Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Environment flags for reproducible and fast container builds
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install project dependencies into virtual environment using layer and BuildKit cache
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy project source files (excluding anything in .dockerignore)
COPY . /app

# Complete synchronization with application package installed
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# ==============================================================================
# Stage 2: Minimal runtime stage
# ==============================================================================
FROM python:3.14-slim AS runner

# Python runtime configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create dedicated non-root user and group (UID/GID 10001) for security hardening
RUN groupadd --system --gid 10001 appgroup && \
    useradd --system --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin appuser

# Copy application and pre-built virtual environment from builder stage
COPY --from=builder --chown=appuser:appgroup /app /app

# Drop root privileges and switch to unprivileged user
USER appuser

# Expose HTTP service port
EXPOSE 8000

# Start FastAPI application listening on 0.0.0.0 for external container ingress
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
