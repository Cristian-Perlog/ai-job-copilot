# Architecture

How AI Job Application Copilot is built. This document describes **what exists
today** and **what is decided but not yet built** — it never claims an unbuilt
thing exists. Each item is marked **Implemented** or **Planned (Phase N)** so the
gap between intent and code is always honest. Significant decisions live in
[Architecture Decision Records](./adr/); AI-specific decisions live in
[ai-practices.md](./ai-practices.md).

---

## Overview

The product is a per-user job-application tracker whose wedge is frictionless
capture (paste a URL or posting text → an LLM drafts the application). See
[product.md](./product.md) and [roadmap.md](./roadmap.md).

**Implemented today**

- FastAPI backend (`backend/app`) with a versioned `/api/v1` API.
- PostgreSQL as the system of record, accessed via SQLAlchemy 2.0.
- Cross-cutting baseline: request-ID middleware, JSON logging, a standard error
  envelope, and a liveness/readiness health split.
- `uv` for dependency management; a multi-stage `Dockerfile`; a `docker-compose.yml`
  with exactly two services — `db` and `backend`.
- pytest suite covering health, the error envelope, request-ID propagation, and
  CORS-on-500 behavior.

**Planned, per roadmap**

- Phase 1: domain models + migrations, Google auth → backend session, CRUD +
  dashboard endpoints, CSV import / CSV+JSON export, Next.js frontend.
- Phase 2: the paste-to-capture AI endpoint, shipping with per-user rate
  limits/quotas and an `ai_generations` audit table.
- Phase 3: one documented AWS IaC deploy, then cheap PaaS hosting for the live demo.

There is **no message queue, worker, or Redis** in the system, and none is
planned for the MVP. (See *Background processing* below — this corrects an earlier
draft of this document that described services which were never built.)

---

## Components

### Backend (FastAPI) — Implemented

- Versioned REST API under `/api/v1`. OpenAPI docs at `/docs` in non-production;
  disabled in production.
- **Sync** SQLAlchemy with `psycopg2`; route handlers are plain `def` and run in
  FastAPI's threadpool. This is a deliberate, documented invariant — see
  [ADR-0002](./adr/0002-sync-sqlalchemy.md).
- Layering: thin **routers** → **services** (business logic) → **scoped-query
  helpers** that enforce per-user ownership at the SQL level. See
  [ADR-0003](./adr/0003-layering-scoped-queries.md). (Routers + health exist
  today; the service and scoped-query layers land with Phase 1 models.)

### Frontend (Next.js + TypeScript) — Planned (Phase 1)

- Google sign-in → backend-minted session (see auth below).
- Pages: dashboard, applications list, application create/edit/detail, interviews.
- Designed empty states; a fetch layer with real loading/error states.
- Not yet in the repo: `frontend/` is added when Phase 1 begins.

### Database (PostgreSQL) — partially Implemented

- Postgres 16 runs in compose today; the connection, engine, and Alembic
  migrations are wired. No domain tables exist yet.
- Core tables **Planned (Phase 1)**: `users`, `job_applications`, `interviews`,
  `application_status_history`.
- `ai_generations` audit table **Planned (Phase 2)**, shipping with the first AI
  endpoint (see [ai-practices.md](./ai-practices.md)).

### Background processing — none in MVP (deliberate)

There is no Celery, no Redis, no worker. Nothing in the MVP needs a queue.

- When capture ships (Phase 2), any deferred work starts with FastAPI
  **`BackgroundTasks`** in-process.
- A real queue (Redis/Celery) is introduced **only if** a measured async need
  emerges (e.g. slow batch extraction) — never speculatively.

---

## API contract (cross-cutting)

- **Versioning** — all endpoints under `/api/v1` (`settings.api_v1_prefix`).
  **Implemented.**
- **Error envelope** — every error response is
  `{"error": {"code": str, "message": str, "request_id": str}}`. Internal details
  are never leaked; unhandled exceptions become a generic `internal_error` 500.
  **Implemented** (`app/core/errors.py`).
- **Request-ID** — middleware reads `X-Request-ID` or generates a uuid4, threads
  it through logs, and echoes it on the response header. **Implemented**
  (`app/core/middleware.py`).
- **Health split** — `GET /api/v1/health/live` (liveness, no DB) and
  `GET /api/v1/health/ready` (readiness, runs `SELECT 1`; 503 envelope with code
  `not_ready` on failure). **Implemented** (`app/api/v1/health.py`).
- **Pagination envelope** — list endpoints return
  `{"items": [...], "total": int, "limit": int, "offset": int}`.
  **Decided; Planned (Phase 1)** — not yet built.

---

## Auth & per-user scoping

- **Auth** — the frontend does Google sign-in, gets a Google ID token, and POSTs
  it once to `/api/v1/auth/google`; the backend verifies it and mints an opaque,
  server-side session in an httpOnly + Secure + SameSite=Lax cookie. Full
  rationale and the rejected NextAuth-owned-session alternative are in
  [ADR-0001](./adr/0001-auth-backend-minted-session.md). **Planned (Phase 1)**;
  the CORS pieces it depends on (explicit origin + credentials) are Implemented.
- **Per-user scoping** — the #1 vulnerability class for this app shape is IDOR.
  Every query touching an owned resource goes through a scoped-query helper that
  *requires* `current_user_id` and filters at the SQL level; cross-user access
  returns **404, not 403** (no existence leak). Ownership tests are required for
  every owned-resource endpoint. See
  [ADR-0003](./adr/0003-layering-scoped-queries.md). **Planned (Phase 1).**

---

## Data conventions

These are settled now so the Phase 1 schema lands consistent.

- **Timestamps** — UTC everywhere, stored as `TIMESTAMPTZ`. A `created_at` /
  `updated_at` mixin on every table.
- **Naming convention** — a SQLAlchemy `naming_convention` is set on the
  declarative `Base` so Alembic autogenerate produces stable constraint/index
  names. **Implemented** (`app/core/db.py`).
- **Application status state machine** — `wishlist → applied → interviewing →
  offer | rejected`, with explicit allowed transitions enforced in the service
  layer. Every transition writes an `application_status_history` row, so the
  pipeline timeline is real data, not a single mutable field. **Planned (Phase 1).**
- **Deletes** — **hard delete**, no soft-delete flag. FK `ON DELETE CASCADE` from
  every user-owned table means deleting a user erases their data (right-to-erasure
  designed in). Status history captures the pipeline trail; we do not also keep
  tombstoned rows. **Planned (Phase 1).**

---

## Observability

- **JSON logs** to stdout, one line per record, carrying the request id.
  **Implemented** (`app/core/logging.py`).
- **Request IDs** propagated through logs and responses. **Implemented.**
- **Sentry** initialized only when `SENTRY_DSN` is set — off by default.
  **Implemented** (`app/main.py`).
- **Deliberately deferred** — metrics and distributed tracing. Logs + request IDs
  + Sentry are enough at this scale; revisit if there is real volume.

---

## Security baseline

- **CORS** — `allow_origins` is the single explicit `settings.frontend_origin`
  with `allow_credentials=True`; never `*`. **Implemented** (`app/main.py`).
- **Docs gating** — `/docs`, `/redoc`, `/openapi.json` are disabled when
  `ENVIRONMENT=production`. **Implemented.**
- **Session cookie hardening** — httpOnly + Secure + SameSite=Lax; CSRF
  double-submit token on state-changing routes. **Planned (Phase 1)**, see ADR-0001.
- **Rate limiting + per-user quotas** — ship **with** the first AI endpoint, not
  retrofitted. **Planned (Phase 2).**
- **Secrets** — env vars locally (`.env`, never committed), GitHub Actions secrets
  in CI, and SSM/secrets-manager for the AWS exercise. No secrets in code.
- **Prompt-injection & SSRF** — the capture feature treats job-posting text/URLs
  as untrusted input. Defenses are summarized in ai-practices.md (untrusted-data
  trust boundary, https-only + private-range rejection before connect, no
  redirect-following to private ranges, timeouts, size and content-type caps).
  **Planned (Phase 2).**

---

## Local development

- **Run it** — `docker compose up` starts `db` (Postgres 16, loopback-only) and
  `backend` (the FastAPI container, which waits for the db healthcheck). The
  frontend joins compose in Phase 1.
- **Dependencies** — `uv` with a committed `uv.lock`; `uv sync` for a reproducible
  env. The Dockerfile resolves deps with `uv` in a builder stage and runs as an
  unprivileged user.
- **Migrations** — author with `alembic revision --autogenerate`, **review the
  generated script**, then `alembic upgrade head`. The DB URL is injected
  programmatically in `alembic/env.py` from typed settings; post-write hooks
  auto-run `ruff` fix + format on new revisions.
- **Tests** — `pytest` (suite under `backend/tests/`). The health/error tests use
  a stub DB session, so they need no running Postgres.

---

## Deployment

Hybrid: build AWS-ready, do **one** documented AWS deploy as a learning exercise
(Terraform under `infrastructure/`, with AWS Budgets alarms set *before* any
apply, then `terraform destroy`), and run the live demo day-to-day on cheap PaaS
(Vercel + Fly.io/Railway + Neon). Migrations run as an **explicit deploy step
before** the new app version goes live — never on container start. Full rationale,
the cost reasoning, and the rejected always-on stack are in
[ADR-0004](./adr/0004-hybrid-deployment.md). **Planned (Phase 3).**
