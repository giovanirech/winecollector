---
status: pending
title: Export service & routes (JSON + CSV)
type: backend
complexity: medium
dependencies:
  - task_12
  - task_13
---

# Task 16: Export service & routes (JSON + CSV)

## Overview
Honor the "you own your data" promise from ADR-003 by exposing one-click downloads of the full cellar as JSON and CSV. The JSON is the canonical machine-readable contract (English keys, `schema_version=1`); the CSV is the human-readable view (Portuguese header + translated categorical values).

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- The export service MUST live at `src/winecollector/services/export_service.py` and accept `AsyncSession` as input.
- `build_envelope(db) -> ExportEnvelope` MUST return an `ExportEnvelope` with `schema_version=1`, `exported_at` set to UTC now, and `wines` sorted by `id` ascending.
- `build_csv(db) -> bytes` MUST return UTF-8 bytes with the Portuguese header `"nome,vinícola,safra,uvas,região,tipo,classificação,estoque,data_compra"` and translated categorical values via the i18n labels from task_12.
- `GET /export/json` MUST return `application/json` with `Content-Disposition: attachment; filename="adega.json"`.
- `GET /export/csv` MUST return `text/csv; charset=utf-8` with `Content-Disposition: attachment; filename="adega.csv"`.
- Both routes MUST require `current_active_user`.
- The export MUST include every wine in the user's cellar (filters are not applied to exports — the export is always the full archive).
</requirements>

## Subtasks
- [ ] 16.1 Implement `src/winecollector/services/export_service.py` with `build_envelope` and `build_csv`.
- [ ] 16.2 Implement `src/winecollector/routers/exports.py` with the two GET routes.
- [ ] 16.3 Register the exports router in `winecollector.main:app`.
- [ ] 16.4 Add the "Exportar Adega" link to the navbar in `base.html`.

## Implementation Details
See TechSpec section "Language conventions in exports" for the contract and ADR-003 for the rationale of having the export in V1. The CSV writer uses the stdlib `csv` module against an in-memory `io.StringIO`, then encodes UTF-8 bytes for the response.

### Relevant Files
- `src/winecollector/services/export_service.py` — to be created.
- `src/winecollector/routers/exports.py` — to be created.
- `src/winecollector/main.py` — modified to register the exports router.
- `src/winecollector/templates/base.html` — modified to link to the export route.

### Dependent Files
- None downstream — the exports are a terminal feature.

### Related ADRs
- [ADR-003: Exportação JSON/CSV Manual no MVP](adrs/adr-003.md) — drives every requirement of this task.
- [ADR-001: Faseamento Arquivista Primeiro](adrs/adr-001.md) — confirms exports belong in the MVP.

## Deliverables
- Working JSON and CSV downloads.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests for both response formats **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_export_service.py::test_envelope_includes_schema_version_1` — `build_envelope(db).schema_version == 1`.
  - [ ] `tests/unit/test_export_service.py::test_envelope_wines_sorted_by_id` — `[w.id for w in envelope.wines] == sorted(...)`.
  - [ ] `tests/unit/test_export_service.py::test_csv_header_row_is_portuguese` — first line of `build_csv(db)` equals the documented PT-BR header.
  - [ ] `tests/unit/test_export_service.py::test_csv_translates_wine_type` — a wine with `wine_type="red"` appears in the CSV with "Tinto".
- Integration tests:
  - [ ] `tests/integration/test_export_routes.py::test_json_download_returns_application_json` — `GET /export/json` returns content-type `application/json` and parses into an `ExportEnvelope`.
  - [ ] `tests/integration/test_export_routes.py::test_csv_download_returns_text_csv` — `GET /export/csv` returns content-type `text/csv; charset=utf-8`.
  - [ ] `tests/integration/test_export_routes.py::test_export_requires_authentication` — unauthenticated request to either route is rejected.
  - [ ] `tests/integration/test_export_routes.py::test_json_includes_every_wine_in_cellar` — number of wines in the envelope equals the row count in `wines`.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- A user can download both files in one click each, from any page (link in navbar).
- The JSON round-trips through `ExportEnvelope.model_validate(json.loads(...))` without loss.
