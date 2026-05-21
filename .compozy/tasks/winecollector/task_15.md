---
status: pending
title: Add/edit wine flow (scrape, duplicate, manual, rescrape)
type: frontend
complexity: high
dependencies:
  - task_14
---

# Task 15: Add/edit wine flow (scrape, duplicate, manual, rescrape)

## Overview
Build the write-side of the cellar: paste-URL → scrape → confirm form → save, the duplicate prompt that incrementally adds stock, the manual entry tab, the wine edit form, the re-scrape flow, and delete-with-confirmation. This task closes the loop between the scraper (task_11), the wine service (task_13), and the user.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `GET /wines/new` MUST render `templates/wines/form.html` in URL-paste mode by default, with a tab toggle for manual entry.
- `POST /wines/scrape` MUST normalize the input URL, check for duplicates via the wine service, and either return the `partials/duplicate_prompt.html` fragment (if duplicate) or call `scrape_wine` and return `partials/wine_form.html` pre-filled with the result.
- `POST /wines` MUST accept the form, build a `WineCreate`, call `wine_service.add_wine_from_url`, and redirect (303) to the detail page.
- `GET /wines/{id}/edit` MUST render an editable form pre-populated with the current wine fields.
- `POST /wines/{id}` MUST apply a `WineUpdate` via the wine service and redirect to the detail page.
- `POST /wines/{id}/rescrape` MUST accept an optional alternate URL form field; when present, replace `source_url` after re-normalization; otherwise reuse the original `source_url`.
- `POST /wines/{id}/delete` MUST delete the wine via the wine service and redirect to `/`.
- The form MUST visibly reflect `scrape_status` — a success banner, a partial warning, or the failure banner with "Tentar novamente" / "Usar outra URL" buttons.
- Every protected route MUST require `current_active_user`.
</requirements>

## Subtasks
- [ ] 15.1 Extend `src/winecollector/routers/wines.py` with the add/scrape/edit/rescrape/delete endpoints.
- [ ] 15.2 Implement `templates/wines/form.html` with the URL-paste / manual tab toggle (Alpine.js if needed).
- [ ] 15.3 Implement `templates/partials/wine_form.html` (form fragment returned by scrape).
- [ ] 15.4 Implement `templates/partials/duplicate_prompt.html` with the +1 stock button.
- [ ] 15.5 Implement `templates/partials/scrape_result.html` (the banner above the form reflecting `scrape_status`).
- [ ] 15.6 Implement `templates/wines/edit.html` (or reuse form.html with mode flag) for the edit flow.
- [ ] 15.7 Wire the "Tentar novamente" and "Usar outra URL" buttons to the rescrape endpoint.

## Implementation Details
See TechSpec section "API Endpoints" for the full route table including HTMX targets, and the PRD Core Features for the failure/partial UX requirements. The duplicate-prompt flow runs before any scraping HTTP call to avoid redundant network traffic (ADR-002).

### Relevant Files
- `src/winecollector/routers/wines.py` — modified to add write endpoints.
- `src/winecollector/templates/wines/form.html` — to be created.
- `src/winecollector/templates/wines/edit.html` — to be created.
- `src/winecollector/templates/partials/wine_form.html` — to be created.
- `src/winecollector/templates/partials/duplicate_prompt.html` — to be created.
- `src/winecollector/templates/partials/scrape_result.html` — to be created.

### Dependent Files
- `src/winecollector/services/wine_service.py` (task_13) — invoked for create/update/delete/scrape paths.
- `src/winecollector/services/scraping/scraper.py` (task_11) — invoked for scrape and rescrape.

### Related ADRs
- [ADR-002: Deduplicação por URL com Incremento Automático de Estoque](adrs/adr-002.md) — drives the duplicate-prompt flow.
- [ADR-001: Faseamento Arquivista Primeiro](adrs/adr-001.md) — manual fallback is a first-class flow.

## Deliverables
- A complete add/edit/rescrape/delete flow.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests for every documented user flow **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_wines_router_write.py::test_scrape_endpoint_returns_duplicate_prompt_when_url_known` — when the wine service signals a duplicate, the response contains the duplicate-prompt fragment.
  - [ ] `tests/unit/test_wines_router_write.py::test_scrape_endpoint_returns_pre_filled_form_on_success` — when scraping succeeds, the response contains the form fragment with the scraped name visible.
- Integration tests:
  - [ ] `tests/integration/test_add_wine_flow.py::test_add_wine_happy_path` — paste URL → scrape (mocked) → submit → detail page shows the wine.
  - [ ] `tests/integration/test_add_wine_flow.py::test_add_wine_partial_pre_fills_form` — when scrape returns `partial`, the form shows the captured fields and an inline warning.
  - [ ] `tests/integration/test_add_wine_flow.py::test_add_wine_failed_shows_retry_and_alt_url` — when scrape returns `failed`, the response includes the retry and alternate-URL buttons.
  - [ ] `tests/integration/test_add_wine_flow.py::test_add_wine_manual_mode_skips_scrape` — submitting via the manual tab does not call the scraper.
  - [ ] `tests/integration/test_add_wine_flow.py::test_duplicate_url_increments_stock` — pasting an existing URL → confirm +1 → detail page shows incremented stock.
  - [ ] `tests/integration/test_edit_wine.py::test_edit_updates_only_provided_fields` — submitting an edit form with one field changed leaves the others untouched.
  - [ ] `tests/integration/test_rescrape.py::test_rescrape_with_new_url_updates_source_url` — POST with an alternate URL replaces `source_url` after normalization.
  - [ ] `tests/integration/test_delete_wine.py::test_delete_removes_record_and_image_file` — after delete, the row is gone and the image file no longer exists.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- A user can complete the full happy path end-to-end at mobile width.
- Every documented failure path (`partial`, `failed`, duplicate, manual) is reachable through the UI.
