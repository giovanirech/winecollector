---
status: pending
title: Scraper service (httpx + BeautifulSoup)
type: backend
complexity: medium
dependencies:
  - task_08
  - task_09
  - task_10
---

# Task 11: Scraper service (httpx + BeautifulSoup)

## Overview
Implement the single function that owns the wine.com.br scraping contract: `scrape_wine(url) -> WineScrapedData`. Every failure path becomes a `scrape_status` value, never a raised exception that escapes the function. Frozen HTML fixtures drive the parser tests so the suite is offline and stable.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `scrape_wine(url: str) -> WineScrapedData` MUST live at `src/winecollector/services/scraping/scraper.py` and always return a `WineScrapedData`, never raise.
- HTTP fetches MUST use `httpx.AsyncClient` with `timeout=Settings.SCRAPER_TIMEOUT` (default 15s), `User-Agent` from `Settings.SCRAPER_USER_AGENT`, and `follow_redirects=True`.
- HTTP failures (`httpx.HTTPStatusError`, `httpx.RequestError`, `asyncio.TimeoutError`) MUST yield `scrape_status = "failed"` and a logged warning with the URL and status.
- A successful fetch with unparseable HTML MUST yield `scrape_status = "failed"`.
- A successful fetch with the core identity fields (at minimum `name`, `winery`) present MUST yield `scrape_status = "success"`.
- A successful fetch missing one or more core fields MUST yield `scrape_status = "partial"`.
- The parser MUST use `BeautifulSoup(html, "html.parser")` with safe selector helpers — no `.text` / `.find()` calls that assume the element exists.
- The image, when present in the parsed page, MUST be downloaded via httpx and converted via `save_image_as_webp` (task_10) on a worker thread.
- The `aging_potential_years` field MUST be filled by passing the source text through `parse_aging_potential` (task_09).
- The `source_url` of the resulting `WineScrapedData` MUST already be normalized via `normalize_wine_url` (task_09).
</requirements>

## Subtasks
- [ ] 11.1 Implement `src/winecollector/services/scraping/scraper.py` with `fetch_page`, `parse_wine_page`, and the orchestrator `scrape_wine`.
- [ ] 11.2 Implement private safe-selector helpers (`_safe_text`, `_safe_int`).
- [ ] 11.3 Wire `save_image_as_webp` via `asyncio.to_thread`.
- [ ] 11.4 Capture three HTML fixtures in `tests/fixtures/html/` (success, partial, no-image) representing real wine.com.br pages.
- [ ] 11.5 Verify the unit tests cover the documented selector contracts.

## Implementation Details
See TechSpec section "Core Interfaces" for the `WineScrapedData` shape, "Integration Points → wine.com.br" for HTTP rules, and `.claude/rules/scraper.md` for the safe-selector pattern. The function composes the helpers from tasks 09 and 10 — it is the only component that does I/O against the network and the filesystem in concert.

### Relevant Files
- `src/winecollector/services/scraping/scraper.py` — to be created.
- `tests/fixtures/html/wine_page_success.html` — to be created (real wine.com.br page snapshot, all fields).
- `tests/fixtures/html/wine_page_partial.html` — to be created (fields missing).
- `tests/fixtures/html/wine_page_no_image.html` — to be created (no `<img>`).

### Dependent Files
- `src/winecollector/services/wine_service.py` (task_13) — calls `scrape_wine` during `add_wine_from_url`.
- `src/winecollector/routers/wines.py` (task_15) — exposes the scrape trigger HTTP route.

### Related ADRs
- [ADR-001: Faseamento Arquivista Primeiro](adrs/adr-001.md) — defines the V1 field scope.
- [ADR-008: Convert Wine Images to WebP via Pillow on Download](adrs/adr-008.md) — image branch.

## Deliverables
- A working `scrape_wine` function with three documented `scrape_status` outcomes.
- Three HTML fixtures captured from real pages.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests with mocked HTTP **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_scraper.py::test_parse_wine_page_success_fills_every_field` — load `wine_page_success.html`; assert every documented field is non-None and `scrape_status == "success"`.
  - [ ] `tests/unit/test_scraper.py::test_parse_wine_page_partial_marks_status` — load `wine_page_partial.html`; assert `scrape_status == "partial"` and the missing fields are `None`.
  - [ ] `tests/unit/test_scraper.py::test_parse_wine_page_no_image_does_not_fail` — load `wine_page_no_image.html`; assert `image_url is None` and the rest parses normally.
  - [ ] `tests/unit/test_scraper.py::test_aging_potential_is_integer` — `WineScrapedData.aging_potential_years` is an int (or None) — never a string.
- Integration tests:
  - [ ] `tests/integration/test_scraper_http.py::test_404_returns_failed_status` — mock `httpx.AsyncClient.get` to raise `HTTPStatusError(404)`; assert `scrape_status == "failed"` and the function returns rather than raises.
  - [ ] `tests/integration/test_scraper_http.py::test_request_error_returns_failed_status` — mock `httpx.RequestError`; assert `scrape_status == "failed"`.
  - [ ] `tests/integration/test_scraper_http.py::test_successful_fetch_invokes_image_normalizer` — mock the HTTP page + the image fetch; assert `image_path` ends in `.webp` and the file exists on disk.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- `scrape_wine` never raises uncaught exceptions to its caller.
- Real wine.com.br is not touched in any test.
