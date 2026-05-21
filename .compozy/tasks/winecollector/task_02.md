---
status: pending
title: Config & async database wiring
type: backend
complexity: low
dependencies:
  - task_01
---

# Task 02: Config & async database wiring

## Overview
Wire the application to its configuration and the async PostgreSQL engine. Every other backend task depends on `get_session` and the `Settings` object, so this task locks in how secrets are read, how the engine is built, and how Alembic finds the metadata.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- A `Settings` class MUST load every environment variable referenced in TechSpec section "Impact Analysis" via `pydantic-settings`.
- `Settings` MUST refuse to start when `SECRET_KEY` is shorter than 32 characters.
- A single async SQLAlchemy engine MUST be created from `DATABASE_URL` using `asyncpg`.
- A FastAPI dependency `get_session` MUST yield an `AsyncSession` and close it after the request.
- A SQLAlchemy `DeclarativeBase` subclass MUST be exported so models in later tasks share metadata.
- Alembic MUST be configured to read the database URL from the same settings object and to operate against the shared metadata, running migrations in async mode.
- The Alembic `env.py` MUST NOT instantiate a sync engine.
</requirements>

## Subtasks
- [ ] 02.1 Implement `src/winecollector/config.py` with the `Settings` class and a module-level singleton.
- [ ] 02.2 Implement `src/winecollector/database.py` with `Base`, the async engine, sessionmaker, and `get_session` dependency.
- [ ] 02.3 Initialize Alembic (`alembic init`) and rewrite `migrations/env.py` to use the async engine + `Settings`.
- [ ] 02.4 Set `script_location` and bypass DB URL in `alembic.ini` (URL comes from env via `env.py`).
- [ ] 02.5 Verify `alembic current` runs without error against an empty database.

## Implementation Details
Refer to TechSpec section "System Architecture" for the FastAPI/SQLAlchemy 2.0 stack constraints and to `.claude/rules/python-style.md` for the SQLAlchemy 2.0 `Mapped[T]` style. The Alembic async setup follows the official SQLAlchemy async migration cookbook. Settings keys mirror the `.env.example` produced by task_01.

### Relevant Files
- `src/winecollector/config.py` — to be created.
- `src/winecollector/database.py` — to be created.
- `alembic.ini` — to be created.
- `migrations/env.py` — to be created (async-aware).
- `migrations/script.py.mako` — to be created (Alembic default).

### Dependent Files
- Every backend task that imports `get_session` or `Base` depends on this file.

### Related ADRs
- None specific to wiring; general guidance is in `AGENTS.md`.

## Deliverables
- A working async engine reachable from the running container.
- A `get_session` dependency usable in FastAPI routes.
- Alembic configured to run async migrations against the shared metadata.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests for session lifecycle and Alembic invocation **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_config.py::test_settings_loads_from_env` — `Settings()` reads every documented key from a controlled `.env`.
  - [ ] `tests/unit/test_config.py::test_settings_rejects_short_secret_key` — `Settings(SECRET_KEY="x")` raises `ValidationError`.
  - [ ] `tests/unit/test_database.py::test_get_session_yields_async_session` — `get_session()` yields an `AsyncSession`.
- Integration tests:
  - [ ] `tests/integration/test_alembic.py::test_alembic_current_runs` — `alembic current` against the test database returns exit code 0.
  - [ ] `tests/integration/test_database.py::test_session_executes_select_1` — opening a session and executing `SELECT 1` returns 1.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- `alembic upgrade head` is callable (no migrations yet, but the command exits 0).
- `SELECT 1` round-trips through the async engine.
