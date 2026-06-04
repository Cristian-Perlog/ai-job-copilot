---
name: db-migrate
description: Create, review, and apply an Alembic migration for a model change. Use when models change or the user asks for a migration.
---

# db-migrate

Procedure for taking a SQLAlchemy model change to an applied, reversible
Alembic migration. Run every command from `backend/`.

## Steps

1. **Confirm the models are visible to autogenerate.** Alembic compares
   `Base.metadata` (set as `target_metadata` in `alembic/env.py`) against the
   live DB. The model module must be imported so its table is registered on the
   metadata — if a new model isn't imported anywhere on the import path, add the
   import (e.g. in `app/core/db.py` or an `app/models/__init__.py`) or autogenerate
   will silently miss it.

2. **Autogenerate the revision:**

   ```
   uv run alembic revision --autogenerate -m "<imperative summary>"
   ```

   The ruff post-write hooks auto-format the generated file.

3. **Read the generated file** before applying it. Autogenerate is a draft, not
   an answer. Work through the checklist below.

4. **Apply it locally** (start the database first):

   ```
   docker compose up -d db    # from repo root
   uv run alembic upgrade head
   ```

5. **Prove it's reversible:**

   ```
   uv run alembic downgrade -1 && uv run alembic upgrade head
   ```

   If `downgrade` fails or loses data unexpectedly, fix the migration.

6. **Run the tests:** `uv run pytest`.

## Review checklist (work through every item)

- [ ] Only the **expected operations** are present — no drift from unrelated
      model edits, no spurious type changes.
- [ ] Constraint and index names follow the `naming_convention` in
      `app/core/db.py` — **no anonymous / auto-named constraints**.
- [ ] **No destructive operations** (`drop_table`, `drop_column`, type narrowing)
      unless that change was explicitly intended.
- [ ] For a new **NOT NULL** column on a table that may have existing rows, use a
      **`server_default`** (DB-side) rather than only a Python-side default, or
      the upgrade fails on populated tables.
- [ ] New **foreign keys have an index** where the access pattern needs one.
- [ ] `upgrade()` and `downgrade()` are **mirror images** — downgrade actually
      undoes upgrade.
- [ ] Timestamps are `TIMESTAMPTZ` (UTC), consistent with the project convention.
- [ ] **Never edit a migration that has already been applied** to a shared DB —
      add a new revision instead.
