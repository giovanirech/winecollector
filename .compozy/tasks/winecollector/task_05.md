---
status: completed
title: Auth routes, base layout & first-run signup gate
type: backend
complexity: medium
dependencies:
  - task_04
---

# Task 05: Auth routes, base layout & first-run signup gate

## Overview
Expose the public auth surface — login, logout, and the self-closing `/signup` route — alongside the `base.html` layout that every other page extends. This is where the first user is created and the only entry point the app keeps open once the cellar is in use.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `GET /signup` MUST return HTTP 200 with the signup form when the `users` table is empty, and HTTP 404 otherwise.
- `POST /signup` MUST also reject (404) when any user already exists, then create the user and redirect to `/login` with a success flash.
- The login form MUST `POST` to fastapi-users' built-in login route, which sets the JWT cookie from task_04.
- `POST /auth/logout` MUST clear the cookie and redirect to `/login`.
- `templates/base.html` MUST include Tailwind CSS via CDN, HTMX via CDN, the mobile-first viewport meta tag, and a flash-message region listening to the `showToast` event.
- All auth templates MUST be in Portuguese (pt-BR) and pass mobile-first visual checks at 375px width.
- No route in this task can return raw fastapi-users registration JSON to the user — registration is hidden behind the gate.
</requirements>

## Subtasks
- [x] 05.1 Implement `src/winecollector/routers/auth.py` with the signup gate, login page render, logout handler.
- [x] 05.2 Wire fastapi-users' login route under `/auth/login` so it sets the cookie configured in task_04.
- [x] 05.3 Implement `templates/base.html` with Tailwind/HTMX CDN, viewport meta, navbar slot, content block, and flash region.
- [x] 05.4 Implement `templates/auth/login.html` and `templates/auth/signup.html` extending `base.html`.
- [x] 05.5 Add the small dependency `signup_open(db) -> bool` that powers the gate.
- [x] 05.6 Register the auth router in `winecollector.main:app` (custom router included before fastapi-users' so our `/auth/logout` takes precedence over the built-in 204 response).

## Implementation Details
See TechSpec sections "API Endpoints" and "Integration Points" for the gate semantics and ADR-005 for the rationale. The login template uses an HTML form, not HTMX, because fastapi-users' login endpoint expects a standard form post and sets the cookie via response headers.

### Relevant Files
- `src/winecollector/routers/auth.py` — to be created.
- `src/winecollector/auth/dependencies.py` — modified to export `signup_open`.
- `src/winecollector/templates/base.html` — to be created.
- `src/winecollector/templates/auth/login.html` — to be created.
- `src/winecollector/templates/auth/signup.html` — to be created.
- `src/winecollector/main.py` — modified to include the auth router and configure Jinja2 templates.

### Dependent Files
- All future pages — extend `base.html`.
- Routes that require auth (tasks 14-16) — rely on the login flow established here.

### Related ADRs
- [ADR-004: Cookie-Based JWT Transport for HTMX/Jinja2 UI](adrs/adr-004.md) — login posts a form, server sets the cookie.
- [ADR-005: First-Run Signup Screen with Self-Closing Registration](adrs/adr-005.md) — defines the gate semantics.

## Deliverables
- A user can sign up once via the browser; subsequent `/signup` requests return 404.
- Login sets the cookie; logout clears it.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests covering the signup → login → logout cycle **(REQUIRED)**.

## Tests
- Unit tests:
  - [x] `tests/unit/test_signup_gate.py::test_signup_open_true_when_users_empty` — `signup_open(session)` returns `True` with no users.
  - [x] `tests/unit/test_signup_gate.py::test_signup_open_false_after_first_user` — returns `False` once a user row exists.
- Integration tests:
  - [x] `tests/integration/test_auth_flow.py::test_signup_creates_first_user` — `POST /signup` with valid form data creates a user and redirects to `/login`.
  - [x] `tests/integration/test_auth_flow.py::test_signup_returns_404_after_first_user` — once one user exists, `GET /signup` returns 404.
  - [x] `tests/integration/test_auth_flow.py::test_login_sets_jwt_cookie` — `POST /auth/login` with correct credentials returns 204 and sets the `winecollector_auth` cookie.
  - [x] `tests/integration/test_auth_flow.py::test_logout_clears_jwt_cookie` — `POST /auth/logout` clears the cookie.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- A fresh database walks through signup → login → logout end-to-end via the browser at mobile width.
- `/signup` returns 404 immediately after the first user is created in the same test run.
