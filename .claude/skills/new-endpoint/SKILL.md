---
name: new-endpoint
description: Add a new API endpoint following project conventions (router -> service -> scoped query, error envelope, ownership tests). Use when adding routes.
---

# new-endpoint

How to add an API endpoint so it matches the project's conventions. The
architecture is layered: **router -> service -> scoped query** (see
`docs/adr/0003-layering-scoped-queries.md`).

## Conventions

- **Sync handlers only.** Every route handler is a sync `def`, never `async def`
  (ADR-0002).
- **Router placement.** Put the `APIRouter` in `app/api/v1/<resource>.py` and
  register it in `app/api/v1/router.py` via `api_router.include_router(...)`.
- **Schemas.** Define Pydantic request and response models (separate from ORM
  models). The handler accepts/returns schemas, not raw ORM objects.
- **Service layer.** Business logic lives in a service function, not in the
  handler. The handler validates input, calls the service, shapes the response.
- **Scoped queries (ownership).** All access to an owned resource goes through a
  scoped-query helper that takes `current_user_id`. A row owned by another user
  is **not found**: return **404**, never 403 (don't leak existence).
- **Pagination.** List endpoints return the pagination envelope
  `{"items", "total", "limit", "offset"}`.
- **Errors.** Raise `HTTPException`; the registered exception handlers render the
  error envelope `{"error": {"code", "message", "request_id"}}`. Don't hand-build
  error JSON in the handler.
- **Timestamps.** UTC `TIMESTAMPTZ`; `created_at`/`updated_at` come from the mixin.

## TDD order (write tests first)

1. **Ownership test** — user A cannot read/modify user B's resource (expect 404).
2. **Happy-path test** — the endpoint does what it should for the owner.
3. Watch both fail, then implement handler + service + scoped query until green.

Tests must not need a real DB or `.env`: use dependency overrides. Follow the
patterns in `backend/tests/conftest.py` (the `make_client` / `get_db` override).

## References

- `docs/adr/0003-layering-scoped-queries.md` — the layering + ownership rule.
- `backend/tests/conftest.py` — dependency-override test fixtures.
- `backend/app/api/v1/health.py` — an existing router for shape reference.
