# Roadmap

Ship a usable product quickly (Phase 1), then layer in the capture wedge and production depth. The MVP must be the best-feeling manual tracker *before* any AI is added; the wedge (paste-to-capture) is the first AI feature in Phase 2.

---

## Phase 0 — Repo setup (done)
- Repository created with `backend/` and `docs/`. (`frontend/` and `infrastructure/` are added when their phases begin, not up front.)
- Backend scaffolded: FastAPI app, health endpoint, PostgreSQL via SQLAlchemy, Alembic migrations configured.
- Drafted `product.md`, `architecture.md`, `roadmap.md`.

---

## Phase 0.5 — Foundations (in progress)

Production-grade baseline, on the `foundations` branch. This is the engineering-learning half of the dual goal paying off early — CI and observability live here, not bolted on at the end.

- Docs revision: `product.md` + `roadmap.md` aligned to the capture wedge and the narrowed vision.
- `uv` for dependency management and reproducible installs.
- Config / environment handling cleaned up (typed settings, no secrets in code).
- Structured **JSON logging**, **request-ID** propagation, a consistent **error-envelope** response shape, and a **health live/ready split** (liveness vs. readiness).
- Test scaffold (pytest) wired and runnable.
- **Dockerfile** + hardened **docker-compose** for local dev.
- `CLAUDE.md` and Claude Code project tooling.
- **pre-commit** hooks, **GitHub Actions CI** (lint + tests + build), **Dependabot**.

Deliverable: a clean, observable, CI-backed baseline to build features on.

---

## Phase 1 — MVP (usable daily tracker, no AI yet)

### 1. Backend
- Models + migrations: `users`, `job_applications`, `interviews`, `application_status_history`.
- Auth: Google ID token verified by the backend, exchanged for a **backend-minted httpOnly session** (see `docs/adr/0001`).
- CRUD + dashboard endpoints, with **pagination** and strict **per-user scoping** on every query.
- **CSV import** (spreadsheet migration path) and **CSV / JSON export** (data-portability / trust).
- Tests for the critical flows.

Deliverable: working API + schema locally, fully per-user isolated.

> No Celery / Redis in the MVP. Nothing here needs a queue.

### 2. Frontend (Next.js + TypeScript)
- Auth UI (Google sign-in → backend session).
- Pages: dashboard, applications list, application create/edit/detail, interviews.
- **Designed empty states** — a new user is onboarded toward capture/import, never shown a dead all-zeros dashboard.
- Fetch layer with real loading / error states.

Deliverable: MVP UI fully functional against the local API.

### 3. Local production experience
- `docker compose up` brings up frontend + backend + Postgres.

Deliverable: the whole MVP runs locally with one command. (CI and observability already exist from Phase 0.5.)

---

## Phase 2 — Capture wedge + first AI feature

### 4. Paste-to-capture (the flagship)
- Endpoint: paste a **job URL** or **posting text** → LLM extracts company, role, location, tech stack, salary.
- Returns a **draft** application with a required **confirm step** before save (human in the loop).
- Ship operational guardrails **with this first AI endpoint**: per-user **rate limiting + quotas**, and an **`ai_generations` audit table** (track cost/usage from the first call).

Deliverable: capture an application from a link or pasted text in seconds — the single feature most likely to move the north-star metric.

### 5. Async only if needed
- Start with FastAPI **BackgroundTasks** for any deferred work.
- Introduce a real queue (Redis/Celery) **only if** a genuine async need emerges (e.g. slow batch extraction). Don't add the queue speculatively.

---

## Phase 3 — Cloud deployment (hybrid: learn it, then run cheap)

Deployment serves both goals without burning money on an idle cloud bill.

### 6. Infrastructure-as-code, one documented deploy
- **Terraform** IaC under `infrastructure/`.
- Stand up **AWS Budgets** alarms at **$10 / $25 / $50 BEFORE any `apply`**.
- Do ONE full, documented AWS deploy as a learning exercise, then **`terraform destroy`**.
- Record the cost reasoning: an always-on **ECS + RDS + ElastiCache + ALB + NAT** stack runs roughly **$130–190/month idle**, which is not justifiable for a portfolio demo.

### 7. Cheap day-to-day hosting
- Run the live demo on low-cost PaaS: e.g. **Vercel** (frontend) + **Fly.io / Railway** (backend) + **Neon** (Postgres).

Deliverable: a public demo URL on a near-zero idle cost, plus a real, documented IaC deploy proving the AWS skill.

---

## Phase 4 — Polish (hireability multiplier)
- Deeper integration tests for critical flows.
- Seed / demo data.
- Architecture + deployment diagrams.
- Short demo video / GIFs in the README.

Deliverable: an "interview-ready" repo — easy to understand, easy to demo, clearly engineered.

---

## Stretch / future ideas
- **LeetCode** progress integration.
- **Calendar** integration for interviews.
- **Gmail / inbox parsing** — deferred indefinitely: the restricted Gmail OAuth scopes trigger Google's CASA security audit, an impractical compliance burden for a solo dev. URL/text paste already covers most of the value.
- **Prioritization / scoring** — only if an inbound, un-curated job stream is ever introduced (scoring the user's own picks just restates their inputs).
