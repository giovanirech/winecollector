---
status: pending
title: Healthcheck endpoint & structured logging
type: infra
complexity: low
dependencies:
  - task_02
---

# Task 17: Healthcheck endpoint & structured logging

## Overview
Wrap the application with the minimum observability the TechSpec specifies — a `/health` endpoint that checks the database, plus a logging configuration that switches between human-readable (dev) and JSON (production) based on the `ENVIRONMENT` setting. The Docker healthcheck and any future hosting platform both depend on `/health`.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `GET /health` MUST be a public, unauthenticated route returning HTTP 200 with body `{"status": "ok", "db": "ok"}` when the database `SELECT 1` succeeds.
- `GET /health` MUST return HTTP 503 with body `{"status": "degraded", "db": "<error>"}` when the database is unreachable.
- The logging configuration MUST live at `src/winecollector/logging_config.py` and be applied at app startup.
- When `Settings.ENVIRONMENT == "production"`, logs MUST emit JSON with `time`, `level`, `logger`, `message` and any structured extras.
- When `Settings.ENVIRONMENT != "production"`, logs MUST emit a human-readable format suitable for terminal reading.
- The `docker-compose.yml` from task_01 MUST be updated to use the `/health` endpoint for the `app` service's healthcheck.
</requirements>

## Subtasks
- [ ] 17.1 Implement `src/winecollector/logging_config.py` with the two formatters.
- [ ] 17.2 Apply the logging configuration in `winecollector.main:app` startup.
- [ ] 17.3 Implement `src/winecollector/routers/health.py` with `GET /health`.
- [ ] 17.4 Register the health router in `winecollector.main:app`.
- [ ] 17.5 Update `docker-compose.yml` so the `app` service has a healthcheck hitting `/health`.

## Implementation Details
See TechSpec section "Monitoring and Observability" for the minimum surface and the rationale for not adding metrics/tracing in V1. The `/health` endpoint should not depend on any other router — keep it small enough that it can be reused by uptime monitors later.

### Relevant Files
- `src/winecollector/logging_config.py` — to be created.
- `src/winecollector/routers/health.py` — to be created.
- `src/winecollector/main.py` — modified to apply logging and register the health router.
- `docker-compose.yml` — modified to add the `app` healthcheck.

### Dependent Files
- None — `/health` and logging are terminal concerns.

### Related ADRs
- None — operational concern, not a design decision.

## Deliverables
- A working `/health` endpoint.
- Logging that adapts to `ENVIRONMENT`.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests covering both healthy and degraded states **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_logging_config.py::test_production_uses_json_formatter` — with `ENVIRONMENT=production`, the root logger's first handler uses a JSON formatter.
  - [ ] `tests/unit/test_logging_config.py::test_development_uses_text_formatter` — with `ENVIRONMENT=development`, the formatter is the human-readable one.
- Integration tests:
  - [ ] `tests/integration/test_health.py::test_health_returns_200_when_db_reachable` — `GET /health` against a running test DB returns 200 with `{"status": "ok", "db": "ok"}`.
  - [ ] `tests/integration/test_health.py::test_health_returns_503_when_db_unreachable` — when the session factory is monkeypatched to raise on `SELECT 1`, the endpoint returns 503.
  - [ ] `tests/integration/test_health.py::test_health_is_public_no_auth_required` — `GET /health` without a cookie returns 200, not 401/redirect.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- `docker compose ps` shows the `app` service as healthy once the migrations have run and the DB is reachable.
- Logs render JSON in production and plain text in development.
