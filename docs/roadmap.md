# Roadmap

This roadmap is designed to ship a usable product quickly (Phase 1) and then layer in “production + wow” features (Phase 2+).

---

## Phase 0 — Repo setup (done)
- Create repository structure (`frontend/`, `backend/`, `docs/`, `infrastructure/`)
- Draft `product.md`, `architecture.md`, `roadmap.md`

---

## Phase 1 — MVP (usable daily tool)

### 1. Backend foundation
- FastAPI project setup
- PostgreSQL integration (SQLAlchemy)
- Alembic migrations
- Core models: users, job_applications, interviews
- CRUD endpoints for applications + interviews
- Basic analytics endpoint(s) for dashboard metrics
- Basic tests (pytest)
- API documentation via OpenAPI

Deliverable:
- Working API + DB schema locally via Docker

### 2. Frontend foundation
- Next.js + TypeScript setup
- Auth UI (Google OAuth)
- Pages:
  - Dashboard (basic metrics)
  - Applications list + create/edit
  - Application detail view
  - Interviews view
- API integration (fetch layer, error states)

Deliverable:
- MVP UI fully functional against local API

### 3. Local production experience
- Dockerize frontend + backend + worker
- Docker Compose one-command startup
- GitHub Actions CI (lint + tests + build)

Deliverable:
- `docker compose up` runs the entire system locally

---

## Phase 2 — “Flagship” features (differentiators)

### 4. Background jobs (Redis + Celery)
- Add worker service + Redis broker
- Use async jobs for:
  - analytics snapshot generation
  - AI tasks (later)
- Add a simple job status table if needed

Deliverable:
- At least one background task running reliably

### 5. Smart application prioritization
- Add user preference settings (country, salary target, stack, etc.)
- Implement rules-based scoring:
  - output: priority score + reasons (“explainability”)
- Add a “Recommended Next Actions” panel on dashboard

Deliverable:
- Users can see ranked applications and understand why

### 6. AI Job Coach (scoped)
Pick ONE AI feature first:
- Cover letter generator from job description + resume bullets
OR
- Interview question generator based on role/company

Deliverable:
- One AI-powered feature integrated end-to-end, invoked via background jobs

---

## Phase 3 — Production deployment (AWS)

### 7. AWS deployment
- Container images in ECR
- ECS Fargate services:
  - frontend
  - backend
  - worker
- RDS Postgres
- ElastiCache Redis
- Secrets in SSM/Secrets Manager
- CloudWatch logs + health checks
- Domain + HTTPS (optional)

Deliverable:
- Public URL with production deployment

---

## Phase 4 — Polish (hireability multiplier)

### 8. Quality improvements
- More tests (integration tests for critical flows)
- Rate limiting / basic abuse protection
- Better error handling + logging
- Observability (Sentry or OpenTelemetry optional)
- Performance improvements (indexes, caching if needed)

### 9. Documentation & demo
- Architecture diagram(s)
- Deployment diagram(s)
- Seed demo data
- Short demo video/GIFs in README

Deliverable:
- “Interview-ready” repo: easy to understand, easy to demo, clearly engineered

---

## Stretch goals
- Gmail parsing ingestion
- Calendar integration
- LeetCode integration
- Learning-based recommendations (train weights from outcomes)
