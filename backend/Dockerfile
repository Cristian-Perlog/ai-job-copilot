# syntax=docker/dockerfile:1

# ---- Builder stage -------------------------------------------------------
# Resolve dependencies with uv into a self-contained virtualenv. psycopg2-binary
# ships manylinux wheels, so no compiler/build toolchain is required here.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Copy only the dependency manifests first so the (expensive) dependency layer
# is cached and only re-runs when pyproject.toml/uv.lock change.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Now copy the application source. This invalidates only the cheap layers below.
COPY . .

# ---- Runtime stage -------------------------------------------------------
FROM python:3.14-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create an unprivileged user to run the app.
RUN groupadd --system app && useradd --system --gid app --home-dir /app app

# Bring over the resolved virtualenv and the application source from the builder.
COPY --from=builder --chown=app:app /opt/venv /opt/venv
COPY --from=builder --chown=app:app /app /app

USER app

EXPOSE 8000

# No curl in the slim image; use the venv's python + urllib for the probe.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/live', timeout=4)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
