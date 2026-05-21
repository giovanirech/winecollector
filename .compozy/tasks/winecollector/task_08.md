---
status: pending
title: Pydantic schemas (wine, tasting, export, WineScrapedData)
type: backend
complexity: low
dependencies:
  - task_07
---

# Task 08: Pydantic schemas (wine, tasting, export, WineScrapedData)

## Overview
Author the Pydantic v2 schemas that mediate every boundary in the app: scraping output, route input/output, and export envelope. Locking these contracts now keeps the scraper, the wine service, and the export service free to evolve in parallel.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `WineScrapedData` MUST match the canonical interface in TechSpec section "Core Interfaces" field-for-field (English identifiers, all optional except `scrape_status`).
- `WineCreate` MUST capture every user-editable field plus `source_url`, `purchased_at`, and `stock`.
- `WineUpdate` MUST allow partial updates (every field optional).
- `WineResponse` MUST set `model_config = ConfigDict(from_attributes=True)` for use with the SQLAlchemy `Wine` model.
- `WineFilterParams` MUST model the cellar filters (search term, wine_type, sweetness, in_stock, sort).
- `TastingCreate`, `TastingUpdate`, `TastingResponse` MUST mirror the `WineTasting` model.
- `ExportEnvelope` MUST include `schema_version: int = 1`, `exported_at: datetime`, `wines: list[ExportedWine]`.
- All schemas MUST live under `src/winecollector/schemas/` with one file per resource.
</requirements>

## Subtasks
- [ ] 08.1 Implement `src/winecollector/schemas/__init__.py` exporting public names.
- [ ] 08.2 Implement `src/winecollector/schemas/wine.py` (`WineScrapedData`, `WineCreate`, `WineUpdate`, `WineResponse`, `WineFilterParams`).
- [ ] 08.3 Implement `src/winecollector/schemas/tasting.py` (`TastingCreate`, `TastingUpdate`, `TastingResponse`).
- [ ] 08.4 Implement `src/winecollector/schemas/export.py` (`ExportedWine`, `ExportEnvelope`).
- [ ] 08.5 Validate that `WineResponse.model_validate(wine_orm_instance)` round-trips correctly.

## Implementation Details
See TechSpec "Core Interfaces" for `WineScrapedData` and "Data Models" for the export envelope shape. All field names follow the English-identifier rule established with the user.

### Relevant Files
- `src/winecollector/schemas/__init__.py` — to be created.
- `src/winecollector/schemas/wine.py` — to be created.
- `src/winecollector/schemas/tasting.py` — to be created.
- `src/winecollector/schemas/export.py` — to be created.

### Dependent Files
- `src/winecollector/services/scraper.py` (task_11) — returns `WineScrapedData`.
- `src/winecollector/services/wine_service.py` (task_13) — uses `WineCreate`, `WineUpdate`, `WineFilterParams`.
- `src/winecollector/services/export_service.py` (task_16) — uses `ExportEnvelope`.
- `src/winecollector/routers/wines.py` (tasks 14, 15) — uses `WineResponse`.

### Related ADRs
- [ADR-002: Deduplicação por URL com Incremento Automático de Estoque](adrs/adr-002.md) — `source_url` is part of the create schema.
- [ADR-003: Exportação JSON/CSV Manual no MVP](adrs/adr-003.md) — defines the `ExportEnvelope` shape.

## Deliverables
- A complete schema layer for wines, tastings, and exports.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests verifying ORM ↔ schema round-tripping **(REQUIRED)**.

## Tests
- Unit tests:
  - [ ] `tests/unit/test_wine_schemas.py::test_wine_scraped_data_defaults_all_optional` — `WineScrapedData()` constructs with no arguments and `scrape_status == "failed"`.
  - [ ] `tests/unit/test_wine_schemas.py::test_wine_create_requires_source_url_and_name` — omitting `source_url` raises `ValidationError`.
  - [ ] `tests/unit/test_wine_schemas.py::test_wine_filter_params_parses_query_string` — `WineFilterParams(...)` accepts both empty and populated filter combinations.
  - [ ] `tests/unit/test_tasting_schemas.py::test_tasting_create_requires_wine_id` — omitting `wine_id` raises `ValidationError`.
  - [ ] `tests/unit/test_export_schemas.py::test_export_envelope_default_schema_version_is_1` — `ExportEnvelope(...).schema_version == 1`.
- Integration tests:
  - [ ] `tests/integration/test_schemas_round_trip.py::test_wine_response_from_orm_instance` — insert a `Wine`, build `WineResponse.model_validate(wine)`, assert every field round-trips.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- All schemas in TechSpec are present and importable.
- ORM ↔ schema round-trip works end-to-end.
