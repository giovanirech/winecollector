---
status: completed
title: WineTasting model & migration
type: backend
complexity: low
dependencies:
  - task_06
---

# Task 07: WineTasting model & migration

## Overview
Ship the `wine_tastings` schema in V1 even though Phase 1 has no UI for it. Per ADR-006, freezing this contract now avoids a rushed schema design during Phase 2 and keeps the JSON export format extensible.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `WineTasting` MUST live at `src/winecollector/models/tasting.py` with the columns from the TechSpec Data Models table.
- `wine_id` MUST be `FOREIGN KEY (wines.id) ON DELETE CASCADE` with an index.
- The `Wine` model MUST expose a `tastings: Mapped[list[WineTasting]]` relationship using `lazy="selectin"`.
- `tasted_at` MUST default to `CURRENT_DATE`.
- The migration MUST be reversible.
- No router, service, or template introduced by this task may reference the model — UI is deferred to Phase 2 per ADR-006.
</requirements>

## Subtasks
- [x] 07.1 Implement `src/winecollector/models/tasting.py` declaring `WineTasting`.
- [x] 07.2 Add the `tastings` relationship on `Wine` (`lazy="selectin"`, `cascade="all, delete-orphan"`).
- [x] 07.3 Export `WineTasting` from `src/winecollector/models/__init__.py`.
- [x] 07.4 Generate the migration via `alembic revision -m "create wine_tastings table"` (autogenerate skipped — no live DB; schema written manually).
- [x] 07.5 Confirm the `ON DELETE CASCADE` and the `wine_id` index — verified by offline `alembic upgrade --sql` and by the cascade integration test.

## Implementation Details
See TechSpec "Data Models" → `wine_tastings` table and ADR-006 for the rationale of shipping the schema without UI. The relationship on `Wine` must use `selectin` loading because all SQLAlchemy access is async — `lazy="select"` would crash in async contexts.

### Relevant Files
- `src/winecollector/models/tasting.py` — to be created.
- `src/winecollector/models/wine.py` — modified to add the `tastings` relationship.
- `src/winecollector/models/__init__.py` — modified to export `WineTasting`.
- `migrations/versions/<timestamp>_create_wine_tastings_table.py` — to be created.

### Dependent Files
- `src/winecollector/schemas/tasting.py` (task_08) — mirrors the model.
- Phase 2 tasting routers and services (out of scope here).

### Related ADRs
- [ADR-006: WineTasting Schema Created in V1, UI Deferred to Phase 2](adrs/adr-006.md) — drives this task entirely.

## Deliverables
- `wine_tastings` table created and reversible.
- `Wine.tastings` available as an empty list for new wines.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests for FK behavior and migration round-trip **(REQUIRED)**.

## Tests
- Unit tests:
  - [x] `tests/unit/test_tasting_model.py::test_tasting_columns_match_techspec` — every documented column is present with the expected type.
  - [x] `tests/unit/test_tasting_model.py::test_wine_id_fk_cascades` — `wine_id` foreign key declares `ondelete="CASCADE"`.
- Integration tests:
  - [x] `tests/integration/test_tastings_migration.py::test_insert_and_select_tasting` — insert a tasting with a valid `wine_id`; `SELECT` returns it.
  - [x] `tests/integration/test_tastings_migration.py::test_delete_wine_cascades_to_tastings` — deleting a wine removes its tastings.
  - [x] `tests/integration/test_tastings_migration.py::test_new_wine_tastings_is_empty_list` — a freshly inserted `Wine` exposes `Wine.tastings == []`.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- `wine_tastings` exists in the schema with the expected FK and index.
- No router or service references `WineTasting` in V1.
