---
status: pending
title: Wine service (CRUD, duplicate detection, stock, search)
type: backend
complexity: high
dependencies:
  - task_08
  - task_09
  - task_11
---

# Task 13: Wine service (CRUD, duplicate detection, stock, search)

## Overview
Implement the central domain service that backs every wine-related route. This service is the only place that queries the `wines` table, so its API is the contract everything else (routers, exports) builds on. It owns CRUD, the URL-based duplicate detection from ADR-002, stock arithmetic, and the ILIKE-based cellar listing from ADR-007.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- The service MUST live at `src/winecollector/services/wine_service.py` and accept `AsyncSession` as a parameter on every function.
- `add_wine_from_url(db, url, scraped) -> AddWineOutcome` MUST normalize the URL via `normalize_wine_url`, check for an existing wine by `source_url`, and either increment that wine's `stock` (returning `was_duplicate=True`) or insert a new row from `scraped` (returning `was_duplicate=False`).
- `get_wine(db, wine_id) -> Wine | None` MUST return the row or `None`; routers raise the 404, not the service.
- `update_wine(db, wine_id, payload) -> Wine` MUST apply only the fields present in `WineUpdate`.
- `delete_wine(db, wine_id) -> None` MUST delete the row AND remove its image file from disk if `image_path` is set.
- `increment_stock(db, wine_id) -> int` and `decrement_stock(db, wine_id) -> int` MUST return the new stock value; `decrement_stock` MUST NOT take the value below 0.
- `list_wines(db, filters: WineFilterParams) -> list[Wine]` MUST apply the ILIKE search across `name`, `winery`, `region` joined by `OR`, plus the `wine_type` / `sweetness` / `in_stock` filters, plus the sort (default `purchased_at DESC`, alternate `vintage DESC`).
- The service MUST raise a domain exception `WineNotFound` when an ID-based op targets a missing row; routers translate this to HTTP 404.
- Every function MUST be `async def`.
</requirements>

## Subtasks
- [ ] 13.1 Define `WineNotFound` and `AddWineOutcome` in `src/winecollector/services/wine_service.py`.
- [ ] 13.2 Implement `add_wine_from_url` with duplicate detection.
- [ ] 13.3 Implement `get_wine`, `update_wine`, `delete_wine`.
- [ ] 13.4 Implement `increment_stock` and `decrement_stock` with the floor at 0.
- [ ] 13.5 Implement `list_wines` with ILIKE + filters + sort.
- [ ] 13.6 Add a small `_delete_image_file(path)` helper that no-ops if the file is already gone.

## Implementation Details
See TechSpec section "Core Interfaces" for the `AddWineOutcome` shape and "Integration Points → URL normalization" for the duplicate-detection contract. The ILIKE pattern is described in ADR-007. All session work uses `await session.execute(select(Wine)...)` per `.claude/rules/python-style.md`.

### Relevant Files
- `src/winecollector/services/wine_service.py` — to be created.
- `src/winecollector/services/exceptions.py` — to be created (`WineNotFound` and other domain exceptions, if a separate file is preferred).

### Dependent Files
- `src/winecollector/routers/wines.py` (tasks 14, 15) — calls every function in this service.
- `src/winecollector/services/export_service.py` (task_16) — uses `list_wines` to assemble the export.

### Related ADRs
- [ADR-002: Deduplicação por URL com Incremento Automático de Estoque](adrs/adr-002.md) — duplicate-detection semantics.
- [ADR-007: ILIKE-Based Search in MVP (No Full-Text Index)](adrs/adr-007.md) — search semantics.

## Deliverables
- A complete wine service backing all wine-related routes.
- A `WineNotFound` domain exception.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests against a real test DB **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_wine_service.py::test_add_wine_from_url_creates_new_wine` — first call inserts; `was_duplicate=False`, `new_stock=1`.
  - [ ] `tests/unit/test_wine_service.py::test_add_wine_from_url_increments_existing` — second call with the same URL returns `was_duplicate=True`, `new_stock=2`, and does not insert.
  - [ ] `tests/unit/test_wine_service.py::test_url_normalization_affects_duplicate_detection` — uppercase variants of the same URL collide.
  - [ ] `tests/unit/test_wine_service.py::test_get_wine_returns_none_for_unknown_id` — `get_wine(db, 9999)` returns `None`.
  - [ ] `tests/unit/test_wine_service.py::test_decrement_stock_floors_at_zero` — calling decrement on a wine with `stock=0` keeps it at 0 and returns 0.
  - [ ] `tests/unit/test_wine_service.py::test_delete_wine_removes_image_file` — deleting a wine whose `image_path` exists removes the file.
- Integration tests:
  - [ ] `tests/integration/test_wine_service_search.py::test_ilike_search_matches_substring_in_name` — `list_wines(filters=WineFilterParams(search="diablo"))` returns the wine named "Casillero del Diablo".
  - [ ] `tests/integration/test_wine_service_search.py::test_filter_in_stock_excludes_zero_stock` — wines with `stock=0` are hidden when `in_stock=True`.
  - [ ] `tests/integration/test_wine_service_search.py::test_sort_by_vintage_desc_orders_newer_first` — vintages 2020 and 2018 return in 2020-first order.
  - [ ] `tests/integration/test_wine_service_search.py::test_filter_by_wine_type_red_returns_only_red` — only wines with `wine_type="red"` are returned when filtered.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- Routers can rely on `WineNotFound` for 404 translation.
- All search/filter combinations from the PRD are exercised by tests.
