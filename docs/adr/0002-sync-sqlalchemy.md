# ADR-0002: Synchronous SQLAlchemy and sync route handlers

## Status

Accepted.

## Context

FastAPI supports both async (`async def` + asyncpg/async sessions) and sync
(`def` + a threadpool) handlers. The workload is solo-developer CRUD over
PostgreSQL: short, transactional reads and writes, no streaming, no websockets,
no high-fan-out I/O. We need to pick one model and hold it as a convention so the
codebase stays consistent.

## Decision

Use **synchronous** SQLAlchemy throughout.

- A sync engine with `psycopg2` (`create_engine`, `pool_pre_ping=True`), already
  wired in `app/core/db.py`.
- **Every route handler is `def`, not `async def`**, so FastAPI runs it in the
  threadpool. This is a documented **invariant**, not a per-endpoint judgement
  call.
- `pool_pre_ping` is on. Explicit pool sizing is **deferred** until we run against
  a managed Postgres with connection limits.

**Revisit trigger:** migrate to asyncpg + async sessions only if a real async need
emerges — e.g. streaming an AI response while touching the DB in the same handler,
or websockets. Until then, async buys nothing.

## Alternatives considered

- **Async SQLAlchemy (asyncpg + async sessions, `async def` handlers).**
  Rejected for now: adds real complexity (async session lifecycle, async test
  fixtures, more Alembic/tooling friction) with zero throughput benefit at this
  scale, and async DB bugs are harder to debug solo.

## Consequences

- Simpler code and debugging; the broad sync ecosystem (Alembic tooling, ordinary
  test fixtures) works without async ceremony.
- Concurrency is bounded by FastAPI's threadpool size — acceptable for the
  expected load, and a known knob if it ever matters.
- When a managed Postgres is introduced, pool sizing must be set deliberately;
  note the Neon/PgBouncer interplay (pooled vs. direct connections) as a future
  check.
- The "all handlers are `def`" rule must be enforced in review; a stray
  `async def` that does blocking DB I/O would block the event loop.
