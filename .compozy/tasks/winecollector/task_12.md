---
status: pending
title: i18n display labels
type: backend
complexity: low
dependencies:
  - task_08
---

# Task 12: i18n display labels

## Overview
Maintain a single source of truth for the English-stored → Portuguese-displayed translations used by templates and the CSV export. Following the project naming rule, English lives in the database and English drives the JSON; Portuguese is generated only at the display layer.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- The label maps MUST live at `src/winecollector/i18n/labels.py`.
- `WINE_TYPE_LABELS` MUST cover every value listed in TechSpec Data Models (`red`, `white`, `rose`, `sparkling`, `semi_sparkling`, `fortified`).
- `SWEETNESS_LABELS` MUST cover `dry`, `off_dry`, `semi_sweet`, `sweet`.
- `SCRAPE_STATUS_LABELS` MUST cover `success`, `partial`, `failed`, `manual`.
- A helper `label(category: str, value: str | None) -> str` MUST return the Portuguese label, or `""` when `value is None`, and the original `value` when the value is not in the map (so missing translations are visible).
- A Jinja2 filter `label_for` MUST expose this helper to templates.
</requirements>

## Subtasks
- [ ] 12.1 Implement `src/winecollector/i18n/__init__.py` exporting the label maps and helper.
- [ ] 12.2 Implement `src/winecollector/i18n/labels.py` with the three maps and the `label` function.
- [ ] 12.3 Register the `label_for` Jinja2 filter in `winecollector.main:app`.
- [ ] 12.4 Document the convention in a module docstring (1-2 lines).

## Implementation Details
See TechSpec section "Data Models" (Display layer paragraph) for the exact PT-BR labels expected. The helper is intentionally tolerant — an unknown value falls back to itself instead of raising, so missing translations show up as readable text in the UI rather than as 500s.

### Relevant Files
- `src/winecollector/i18n/__init__.py` — to be created.
- `src/winecollector/i18n/labels.py` — to be created.
- `src/winecollector/main.py` — modified to register the Jinja2 filter.

### Dependent Files
- Templates from task_14 and task_15 — use `label_for` to display `wine_type`, `sweetness`, `scrape_status`.
- `src/winecollector/services/export_service.py` (task_16) — uses the maps to translate categorical values in the CSV.

### Related ADRs
- [ADR-001: Faseamento Arquivista Primeiro](adrs/adr-001.md) — the PT-BR UI is part of the V1 contract.
- [ADR-003: Exportação JSON/CSV Manual no MVP](adrs/adr-003.md) — CSV uses PT-BR labels.

## Deliverables
- Three label maps + helper + Jinja filter.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- No integration tests required (pure mappings + filter registration).

## Tests
- Unit tests:
  - [ ] `tests/unit/test_labels.py::test_wine_type_red_maps_to_tinto` — `label("wine_type", "red") == "Tinto"`.
  - [ ] `tests/unit/test_labels.py::test_sweetness_off_dry_maps_to_meio_seco` — `label("sweetness", "off_dry") == "Meio seco"`.
  - [ ] `tests/unit/test_labels.py::test_scrape_status_failed_maps_to_falhou` — `label("scrape_status", "failed") == "Falhou"`.
  - [ ] `tests/unit/test_labels.py::test_none_value_returns_empty_string` — `label("wine_type", None) == ""`.
  - [ ] `tests/unit/test_labels.py::test_unknown_value_returns_original` — `label("wine_type", "magenta") == "magenta"`.
  - [ ] `tests/unit/test_labels.py::test_label_for_filter_registered_on_app` — `app.jinja_env.filters["label_for"] is label`.
- Integration tests: not applicable.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- Every categorical value documented in the TechSpec has a Portuguese label.
- Unknown values fall back gracefully without raising.
