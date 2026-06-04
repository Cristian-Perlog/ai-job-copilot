# CLAUDE.md

Guidance for Claude Code working in this repository.

## Project

AI Job Application Copilot is a job-application tracker for early-career software
engineers. The MVP (Phase 1) is the best-feeling *manual* tracker; the
differentiating AI capture wedge — paste a job URL or posting text and an LLM
extracts the fields into a draft you confirm — is the first AI feature and lands
in Phase 2. This repo has a deliberate dual goal, both halves treated as equal
priority: a real product someone would use during a job hunt, and a
production-grade engineering learning project (auth, data modeling, CI,
observability, cloud deploy done the way a strong team would).

Read these before non-trivial work:

- `docs/product.md` — positioning, the wedge, MVP scope.
- `docs/architecture.md` — system design, status transitions, layering.
- `docs/adr/` — accepted decisions (0001 auth, 0002 sync SQLAlchemy, 0003
  scoped queries, 0004 hybrid deployment).
- `docs/roadmap.md` — phases; we are in Phase 0.5 (foundations).
- `docs/ai-practices.md` — rules the first AI feature must follow.

## Stack

- **Backend:** FastAPI + **sync** SQLAlchemy 2 + Alembic + PostgreSQL 16.
- **Deps:** `uv` (lockfile-driven, reproducible installs).
- **Frontend:** Next.js + TypeScript — planned, Phase 1 (not in the repo yet).
- **No Celery / Redis.** Deliberate: nothing in the MVP needs a queue. Start
  with FastAPI `BackgroundTasks` if deferred work appears; a real queue is added
  only if a genuine async need emerges (see `docs/roadmap.md` Phase 2).

## Commands

Run from `backend/` unless noted. `.env` lives at the **repo root**; copy it from
`.env.example` (`Copy-Item .env.example .env`).

- `uv sync` — install all deps including the dev group.
- `uv run pytest` — run the test suite (hermetic; no DB or `.env` needed).
- `uv run ruff check .` — lint. `uv run ruff format .` — format.
- `uv run uvicorn app.main:app --reload` — run the API locally.
- `uv run alembic upgrade head` — apply migrations.
- `uv run alembic revision --autogenerate -m "..."` — generate a migration.
- `docker compose up -d` (from **repo root**) — db + backend.
- `uvx pre-commit install` (from repo root, once) — install the git pre-commit hooks.

## Conventions

- All route handlers are sync `def`, never `async def` (ADR-0002).
- Every owned-resource query goes through a scoped-query helper requiring
  `current_user_id`; cross-user access returns 404 (ADR-0003). Ownership tests
  are required for every owned-resource endpoint.
- Every error response uses the envelope `{"error": {"code", "message", "request_id"}}`.
- All timestamps are UTC `TIMESTAMPTZ`; models get `created_at`/`updated_at` via a mixin.
- Migrations: autogenerate -> **read the generated file** -> upgrade. Never edit
  an applied migration; the `naming_convention` is set in `app/core/db.py` —
  don't bypass it.
- Conventional commits (`feat`/`fix`/`docs`/`chore`/`test`/`refactor`, scope optional).
- Tests must not need a real DB or `.env` — use dependency overrides (see
  `tests/conftest.py`).

## Development loop

- Brainstorm and design before building; the cheapest bug is the one not built.
- Write a plan for any multi-step work before touching code.
- TDD: write the test first, watch it fail, then implement.
- Code review before merge.
- Verify by running it, not by assuming it works.
- Reach for subagents / parallel sessions for multi-file refactors or
  independent workstreams; a plain session is fine otherwise.

## Deferred tooling (revisit triggers)

- **Custom subagents** (`.claude/agents/`): add when the codebase grows distinct
  subsystems that need specialized review.
- **MCP servers** (e.g. a Postgres inspector): add when schema work becomes
  routine enough that live inspection pays for itself.
- **Workflows** (`.claude/workflows/`): add when repeatable multi-agent
  procedures emerge worth codifying.
