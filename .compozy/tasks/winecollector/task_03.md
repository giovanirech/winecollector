---
status: completed
title: User model & initial migration
type: backend
complexity: low
dependencies:
  - task_02
---

# Task 03: User model & initial migration

## Overview
Introduce the `User` model that fastapi-users will own and create the first Alembic migration that materializes the `users` table. This task is the data foundation that the authentication backend (task_04) and signup gate (task_05) rely on.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `User` MUST inherit from `SQLAlchemyBaseUserTableUUID` (fastapi-users) and share `Base` from task_02.
- The model MUST live at `src/winecollector/models/user.py`.
- An Alembic migration MUST create the `users` table with the columns fastapi-users requires (`id` UUID PK, `email` unique, `hashed_password`, `is_active`, `is_superuser`, `is_verified`).
- The migration MUST be reversible (`downgrade()` drops the table).
- Running `alembic upgrade head` on an empty test database MUST create the `users` table with the expected schema.
</requirements>

## Subtasks
- [x] 03.1 Add `src/winecollector/models/__init__.py` exporting `Base` and `User`.
- [x] 03.2 Implement `src/winecollector/models/user.py` extending the fastapi-users base table.
- [x] 03.3 Generate the migration via `alembic revision -m "create users table"` (autogenerate skipped — requires a live DB; the schema is small and was authored manually then verified offline).
- [x] 03.4 Verify the generated migration matches the expected DDL via `alembic upgrade head --sql` and `alembic downgrade --sql head:base`.
- [x] 03.5 Apply the migration to the test database and confirm the schema (covered by `tests/integration/test_users_migration.py`, gated by `WINECOLLECTOR_RUN_DB_TESTS=1`).

## Implementation Details
The User model is the entry point for fastapi-users' SQLAlchemy adapter; see TechSpec section "Data Models" for the high-level contract. Migration file naming should follow the timestamped convention Alembic uses by default.

### Relevant Files
- `src/winecollector/models/__init__.py` — to be created.
- `src/winecollector/models/user.py` — to be created.
- `migrations/versions/<timestamp>_create_users_table.py` — to be created.

### Dependent Files
- `src/winecollector/auth/` (task_04) — imports `User`.
- All future migrations — share the same metadata.

### Related ADRs
- [ADR-005: First-Run Signup Screen with Self-Closing Registration](adrs/adr-005.md) — the `users` table is what the gate inspects.

## Deliverables
- A `User` model usable by fastapi-users.
- An Alembic migration that creates `users` and is reversible.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests verifying the migration applies and the schema matches **(REQUIRED)**.

## Tests
- Unit tests:
  - [x] `tests/unit/test_user_model.py::test_user_inherits_required_columns` — `User.__table__.columns` contains `id`, `email`, `hashed_password`, `is_active`, `is_superuser`, `is_verified`.
  - [x] `tests/unit/test_user_model.py::test_email_column_has_unique_index` — `User.__table__` indicates `email` is unique.
- Integration tests:
  - [x] `tests/integration/test_users_migration.py::test_upgrade_creates_users_table` — applying head migrations creates the `users` table with the expected columns.
  - [x] `tests/integration/test_users_migration.py::test_downgrade_drops_users_table` — downgrading removes the table.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- `alembic upgrade head` creates the `users` table.
- `alembic downgrade base` removes it cleanly.
