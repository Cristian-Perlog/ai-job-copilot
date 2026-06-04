# AI Job Application Copilot

A job-application tracker for early-career software engineers. Its one
differentiator: **you never type an application** — paste a job URL or the
posting text and an LLM extracts the company, role, location, tech stack, and
salary into a draft you confirm in one click. Everything else is a focused,
well-built tracker around that capture core.

This repo has a deliberate **dual goal**, both halves equal priority: a real
product an early-career engineer would actually use during a job search, and a
production-grade engineering learning project — backend design, auth, data
modeling, CI, observability, and a documented cloud deployment done the way a
strong team would do them.

**Status:** Phase 0.5 — foundations (observable, CI-backed baseline). The
capture wedge is the first AI feature and lands in Phase 2. See
[docs/roadmap.md](docs/roadmap.md).

## Tech stack

- **Backend:** FastAPI, sync SQLAlchemy 2 + Alembic, PostgreSQL 16
- **Tooling:** uv (deps), ruff (lint/format), pytest, pre-commit, GitHub Actions
- **Frontend:** Next.js + TypeScript (planned, Phase 1)
- **Runtime / infra:** Docker for local dev; a documented one-off AWS deploy as
  a learning exercise, then low-cost PaaS for the live demo (see
  [docs/adr/0004-hybrid-deployment.md](docs/adr/0004-hybrid-deployment.md))

There is intentionally **no Redis / Celery** — nothing in the MVP needs a queue.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Docker.

```powershell
# 1. Configure environment (.env lives at the repo root)
Copy-Item .env.example .env        # macOS/Linux: cp .env.example .env

# 2. Start Postgres
docker compose up -d db

# 3. Install deps, apply migrations, run the API
cd backend
uv sync
uv run alembic upgrade head        # currently a no-op: no migrations yet
uv run uvicorn app.main:app --reload
```

Then check readiness at <http://localhost:8000/api/v1/health/ready> and the API
docs at <http://localhost:8000/docs>.

Run the tests (hermetic — no database or `.env` required):

```powershell
cd backend
uv run pytest
```

### All-Docker path

Bring up the database and backend together from the repo root:

```powershell
docker compose up -d               # db + backend
```

## Project structure

```
.
├── backend/            # FastAPI app, tests, Alembic, Dockerfile (uv project)
│   ├── app/            # application code (api, core)
│   ├── alembic/        # migration environment
│   └── tests/          # pytest suite (hermetic)
├── docs/               # product, architecture, ADRs, roadmap, AI practices
├── .github/            # CI workflow + Dependabot
├── docker-compose.yml  # db + backend for local dev
└── .env.example        # copy to .env at the repo root
```

## Documentation

- [docs/product.md](docs/product.md) — positioning, the wedge, MVP scope
- [docs/architecture.md](docs/architecture.md) — system design and conventions
- [docs/adr/](docs/adr/) — accepted architecture decisions
- [docs/roadmap.md](docs/roadmap.md) — phased delivery plan
- [docs/ai-practices.md](docs/ai-practices.md) — rules for the AI features
- [CLAUDE.md](CLAUDE.md) — guidance for Claude Code in this repo

## License

MIT — see [LICENSE](LICENSE).
