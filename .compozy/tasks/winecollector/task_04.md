---
status: pending
title: Authentication backend (cookie JWT)
type: backend
complexity: medium
dependencies:
  - task_03
---

# Task 04: Authentication backend (cookie JWT)

## Overview
Wire fastapi-users with the `CookieTransport` + `JWTStrategy` combination chosen in ADR-004, plus the `UserManager`, the `current_active_user` dependency, and the SQLAlchemy user database adapter. This task delivers the auth primitives that every protected route depends on without yet exposing any HTTP routes (those land in task_05).

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- A single `AuthenticationBackend` MUST combine `CookieTransport` and `JWTStrategy`.
- The JWT secret and expiration MUST come from `Settings` (no hardcoded values).
- The cookie MUST be `HttpOnly`, `SameSite=Lax`, and `Secure` whenever `ENVIRONMENT == "production"`.
- A `UserManager` MUST inherit `BaseUserManager` and override `on_after_register` for logging.
- A `get_user_db` async dependency MUST wrap `SQLAlchemyUserDatabase` with the session from `get_session`.
- A `FastAPIUsers` instance MUST expose `current_active_user` for downstream dependencies.
- No public registration route MUST be mounted — the default fastapi-users register router is intentionally omitted (the signup flow is custom in task_05).
</requirements>

## Subtasks
- [ ] 04.1 Add `src/winecollector/auth/__init__.py` exporting public names.
- [ ] 04.2 Implement `src/winecollector/auth/user_db.py` with `get_user_db`.
- [ ] 04.3 Implement `src/winecollector/auth/manager.py` with `UserManager` and `get_user_manager`.
- [ ] 04.4 Implement `src/winecollector/auth/backend.py` with `CookieTransport`, `JWTStrategy`, and the assembled `AuthenticationBackend`.
- [ ] 04.5 Implement `src/winecollector/auth/dependencies.py` exporting `fastapi_users` and `current_active_user`.
- [ ] 04.6 Verify the cookie attributes adapt to `ENVIRONMENT` from settings.

## Implementation Details
Follow TechSpec section "Integration Points" (no external services here, only internal libraries) and ADR-004 for transport configuration. The structure mirrors the fastapi-users SQLAlchemy quickstart but never mounts the default register router. Read the auth dependencies into routes via `Depends(current_active_user)`.

### Relevant Files
- `src/winecollector/auth/__init__.py` — to be created.
- `src/winecollector/auth/user_db.py` — to be created.
- `src/winecollector/auth/manager.py` — to be created.
- `src/winecollector/auth/backend.py` — to be created.
- `src/winecollector/auth/dependencies.py` — to be created.

### Dependent Files
- `src/winecollector/routers/auth.py` (task_05) — uses the backend + dependencies.
- Every protected router (tasks 14, 15, 16, etc.) — relies on `current_active_user`.

### Related ADRs
- [ADR-004: Cookie-Based JWT Transport for HTMX/Jinja2 UI](adrs/adr-004.md) — defines the transport choice.
- [ADR-005: First-Run Signup Screen with Self-Closing Registration](adrs/adr-005.md) — explains why the default register router is omitted.

## Deliverables
- A working `AuthenticationBackend` and `current_active_user` dependency.
- A `UserManager` that logs registrations.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests verifying token round-trip and cookie attributes **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_auth_backend.py::test_jwt_strategy_uses_settings_secret` — strategy reads `SECRET_KEY` from `Settings`.
  - [ ] `tests/unit/test_auth_backend.py::test_cookie_secure_flag_follows_environment` — `secure=True` when `ENVIRONMENT=production`, `False` otherwise.
  - [ ] `tests/unit/test_user_manager.py::test_on_after_register_logs_event` — `on_after_register` emits an INFO log with the user email.
- Integration tests:
  - [ ] `tests/integration/test_auth_protection.py::test_unauthenticated_request_to_protected_route_returns_401_or_redirect` — a route that depends on `current_active_user` rejects unauthenticated requests.
  - [ ] `tests/integration/test_auth_protection.py::test_valid_cookie_grants_access` — a request with a valid JWT cookie returns 200.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- `current_active_user` can be injected into any route declaration.
- The cookie carries the JWT in dev (over HTTP) and only over HTTPS in production.
