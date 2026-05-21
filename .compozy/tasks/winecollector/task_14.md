---
status: pending
title: Cellar overview & wine detail UI
type: frontend
complexity: high
dependencies:
  - task_05
  - task_12
  - task_13
---

# Task 14: Cellar overview & wine detail UI

## Overview
Build the read-side of the application — the cellar overview at `/` with search, filters, and sort, and the wine detail page with the stock controls. These are the pages the user lands on every time they consult the cellar before opening a bottle.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `GET /` MUST render the cellar overview with the wine cards (image, name, winery, vintage, stock) in mobile-first layout.
- `GET /wines` MUST share the same handler and inspect the `HX-Request` header to decide whether to render the full page or just the cellar fragment — used by the search/filter HTMX swaps.
- `GET /wines/{id}` MUST render the wine detail page with every field shown using `label_for` for categorical values.
- `POST /wines/{id}/stock/increment` and `POST /wines/{id}/stock/decrement` MUST return the `partials/stock_counter.html` fragment with the updated number.
- Every page MUST extend `base.html` from task_05.
- Every protected route MUST require `current_active_user` (task_04 dependency).
- All UI labels MUST be Portuguese; categorical values rendered via `label_for`.
- Search input MUST use HTMX (`hx-get`, `hx-trigger="keyup changed delay:300ms"`, `hx-target="#cellar-list"`).
- Filters MUST use HTMX form submission targeting the same fragment.
</requirements>

## Subtasks
- [ ] 14.1 Implement `src/winecollector/routers/pages.py` exposing `GET /`, `GET /wines`, `GET /wines/{id}`.
- [ ] 14.2 Implement `src/winecollector/routers/wines.py` exposing the stock increment/decrement routes.
- [ ] 14.3 Implement `templates/wines/index.html` (full page extending `base.html`) and `templates/partials/cellar_list.html` (fragment).
- [ ] 14.4 Implement `templates/wines/detail.html` with stock controls.
- [ ] 14.5 Implement `templates/partials/wine_card.html` (used in the cellar list) and `partials/stock_counter.html` (returned by stock routes).
- [ ] 14.6 Add a small CSS file `static/css/app.css` for any Tailwind overrides needed by the cards.
- [ ] 14.7 Register the routers with `winecollector.main:app` and mount `/static`.

## Implementation Details
See TechSpec section "API Endpoints" for the route table and "User Experience" in the PRD for the mobile-first card layout. The HX-Request inspection pattern lets every URL deep-link to the full page while still supporting partial swaps for HTMX.

### Relevant Files
- `src/winecollector/routers/pages.py` — to be created.
- `src/winecollector/routers/wines.py` — to be created (write endpoints added in task_15).
- `src/winecollector/templates/wines/index.html` — to be created.
- `src/winecollector/templates/wines/detail.html` — to be created.
- `src/winecollector/templates/partials/cellar_list.html` — to be created.
- `src/winecollector/templates/partials/wine_card.html` — to be created.
- `src/winecollector/templates/partials/stock_counter.html` — to be created.

### Dependent Files
- `src/winecollector/templates/wines/form.html` (task_15) — also extends `base.html`.
- `src/winecollector/routers/exports.py` (task_16) — linked from the navbar in `base.html`.

### Related ADRs
- [ADR-004: Cookie-Based JWT Transport for HTMX/Jinja2 UI](adrs/adr-004.md) — routes protected via cookie auth.
- [ADR-007: ILIKE-Based Search in MVP (No Full-Text Index)](adrs/adr-007.md) — search semantics surfaced by this UI.

## Deliverables
- A working cellar overview at `/` with search, filters, sort.
- A working wine detail page at `/wines/{id}` with stock controls.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests for the read-side flow **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_pages_router.py::test_index_uses_filter_params_from_query` — `GET /?search=foo&wine_type=red&sort=vintage` constructs a `WineFilterParams` with those values.
  - [ ] `tests/unit/test_pages_router.py::test_index_returns_fragment_on_hx_request` — request with `HX-Request: true` returns the partial, not the full page.
- Integration tests:
  - [ ] `tests/integration/test_cellar_view.py::test_unauthenticated_request_redirected_to_login` — `GET /` without cookie redirects to `/login`.
  - [ ] `tests/integration/test_cellar_view.py::test_authenticated_request_shows_cellar` — authenticated `GET /` includes every wine name in the response body.
  - [ ] `tests/integration/test_cellar_view.py::test_htmx_search_returns_partial` — `GET /wines?search=diablo` with `HX-Request: true` returns only the cellar fragment.
  - [ ] `tests/integration/test_wine_detail.py::test_detail_page_shows_all_fields` — `GET /wines/{id}` displays each scraped field via `label_for` where applicable.
  - [ ] `tests/integration/test_stock_controls.py::test_increment_updates_counter_fragment` — `POST /wines/{id}/stock/increment` returns `partials/stock_counter.html` with the new value.
  - [ ] `tests/integration/test_stock_controls.py::test_decrement_does_not_go_below_zero` — calling decrement on stock-0 returns 0.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- The cellar overview is usable end-to-end with HTMX search and filters at 375px width.
- The wine detail page surfaces every field captured by the scraper.
