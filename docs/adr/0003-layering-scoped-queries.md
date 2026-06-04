# ADR-0003: Layering — routers → services → scoped queries

## Status

Accepted.

## Context

This is a multi-tenant app where every row belongs to a user. The dominant
vulnerability class for this shape is **IDOR**: a user fetching, editing, or
deleting another user's resource by guessing or supplying its id. We need an
architecture where per-user scoping is a structural primitive, not a thing each
endpoint remembers to do by hand.

## Decision

Three layers, with the scoping enforced in a dedicated seam.

1. **Routers** — thin: request validation, dependency wiring, response shaping.
   No business logic, no raw ORM queries.
2. **Services** — business logic and domain rules (e.g. status-transition
   validation).
3. **Scoped-query helpers** — the per-user-scoping **security primitive**. Every
   query touching an owned resource goes through a helper that **requires**
   `current_user_id` and filters at the SQL level, e.g.
   `get_application_or_404(db, user_id, application_id)`.

Supporting rules:

- A `get_current_user` FastAPI dependency resolves the session cookie → `User` and
  supplies the `current_user_id` the helpers require.
- Cross-user access returns **404, not 403** — a 403 would leak that the resource
  exists. This existence-hiding choice is intentional and documented here.
- **Ownership tests are required** for every owned-resource endpoint: fetching
  another user's resource id must return 404.

## Alternatives considered

- **A full repository layer for every entity.** Rejected: ceremonial
  pass-through wrappers around plain CRUD that add indirection without value at
  this size.
- **Routers calling the ORM directly.** Rejected: there is then no single seam to
  enforce the scoping invariant, so every endpoint becomes an IDOR risk.

## Consequences

- Per-user scoping is enforced in one small, auditable layer instead of scattered
  across handlers.
- The 404-on-cross-user rule must be applied uniformly, and tests must assert it.
- A little more structure than direct-ORM routers, but far less than a full
  repository pattern — the seam exists exactly where the security boundary is.
