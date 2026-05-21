---
status: completed
title: Wine model & migration
type: backend
complexity: low
dependencies:
  - task_03
---

# Task 06: Wine model & migration

## Overview
Materialize the `Wine` entity — the core of the entire app — with every field listed in the PRD's expanded Core Features and the TechSpec's Data Models section. Once this migration applies, the cellar can hold real records.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- The `Wine` SQLAlchemy model MUST live at `src/winecollector/models/wine.py` using `Mapped[T]` + `mapped_column()` style.
- Every column listed in the TechSpec "Data Models" table for `wines` MUST be present with the documented type and nullability.
- `source_url` MUST have a unique index; `wine_type`, `winery`, and `purchased_at` MUST be indexed.
- `stock` MUST default to 1 and enforce `CHECK (stock >= 0)`.
- `purchased_at` MUST default to `CURRENT_DATE`.
- `created_at` and `updated_at` MUST default to `now()`; `updated_at` MUST update on row modification.
- The Alembic migration MUST be reversible.
- The migration MUST NOT alter the `users` table — append-only.
</requirements>

## Subtasks
- [x] 06.1 Implement `src/winecollector/models/wine.py` declaring `Wine` with every field.
- [x] 06.2 Export `Wine` from `src/winecollector/models/__init__.py`.
- [x] 06.3 Generate the migration via `alembic revision -m "create wines table"` (autogenerate skipped — no live DB; schema written manually).
- [x] 06.4 Add the `CHECK (stock >= 0)` constraint and the four named indexes (`source_url` unique, plus `wine_type`, `winery`, `purchased_at`).
- [x] 06.5 Apply the migration to the test database and confirm the schema (covered by `tests/integration/test_wines_migration.py`; offline `alembic upgrade --sql` also renders the expected DDL).

## Implementation Details
See TechSpec section "Data Models" for the canonical column list (English identifiers, English stored values for categorical fields per the project naming rule). Refer to `.claude/rules/python-style.md` for the SQLAlchemy 2.0 declarative pattern.

### Relevant Files
- `src/winecollector/models/wine.py` — to be created.
- `src/winecollector/models/__init__.py` — modified to export `Wine`.
- `migrations/versions/<timestamp>_create_wines_table.py` — to be created.

### Dependent Files
- `src/winecollector/models/tasting.py` (task_07) — FK targets `wines.id`.
- `src/winecollector/schemas/wine.py` (task_08) — mirrors the model.
- `src/winecollector/services/wine_service.py` (task_13) — queries this table.

### Related ADRs
- [ADR-002: Deduplicação por URL com Incremento Automático de Estoque](adrs/adr-002.md) — drives the `source_url` unique index.
- [ADR-001: Faseamento Arquivista Primeiro](adrs/adr-001.md) — sets the V1 field scope.

## Deliverables
- A working `Wine` model and `wines` table.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- Integration tests asserting the schema and constraints **(REQUIRED)**.

## Tests
- Unit tests:
  - [x] `tests/unit/test_wine_model.py::test_wine_columns_match_techspec` — assert every documented column is present with the expected type and nullability.
  - [x] `tests/unit/test_wine_model.py::test_source_url_is_unique_and_indexed` — `Wine.__table__` has a unique index on `source_url`.
- Integration tests:
  - [x] `tests/integration/test_wines_migration.py::test_insert_minimum_wine_succeeds` — inserting a row with only the not-null fields succeeds and gets defaults applied.
  - [x] `tests/integration/test_wines_migration.py::test_duplicate_source_url_raises_integrity_error` — inserting two wines with the same `source_url` raises `IntegrityError`.
  - [x] `tests/integration/test_wines_migration.py::test_stock_negative_check_blocks_negative_value` — setting `stock = -1` raises `IntegrityError`.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- `\d wines` shows the expected columns, indexes, and constraints.
- Migration is reversible without error.
