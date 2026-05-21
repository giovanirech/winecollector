---
status: pending
title: URL normalizer & aging-potential parser
type: backend
complexity: low
dependencies:
  - task_01
---

# Task 09: URL normalizer & aging-potential parser

## Overview
Implement the two pure functions that the scraper and the wine service both depend on: URL canonicalization (the key for duplicate detection) and aging-potential extraction (the integer driving the future drinking-window heuristic). Pure functions are easy to test exhaustively before any HTTP or DB code exists.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `normalize_wine_url(url: str) -> str` MUST apply the rules from TechSpec section "Integration Points → URL normalization" (lowercase host, drop query/fragment, strip trailing slash, force `https`).
- `normalize_wine_url` MUST raise `ValueError` when the host does not end with `wine.com.br` or the scheme is neither `http` nor `https`.
- `parse_aging_potential(text: str | None) -> int | None` MUST follow the heuristics in TechSpec section "Integration Points → Aging-potential parser" (single int → return; range → upper bound; non-numeric → None; None → None).
- Both functions MUST be importable from `src/winecollector/services/scraping/`.
- Both functions MUST have no side effects (no HTTP, no DB, no filesystem).
</requirements>

## Subtasks
- [ ] 09.1 Create `src/winecollector/services/scraping/__init__.py`.
- [ ] 09.2 Implement `src/winecollector/services/scraping/normalize.py` with `normalize_wine_url`.
- [ ] 09.3 Implement `src/winecollector/services/scraping/parsers.py` with `parse_aging_potential`.
- [ ] 09.4 Author exhaustive table-driven tests for every documented edge case.

## Implementation Details
Both functions are described in TechSpec section "Integration Points". The URL normalizer uses `urllib.parse.urlsplit`; the parser uses `re.findall(r"\d+", text)` with the documented selection rules. Keep both files free of any imports from `winecollector.models` or `winecollector.schemas` to preserve their purity.

### Relevant Files
- `src/winecollector/services/scraping/__init__.py` — to be created.
- `src/winecollector/services/scraping/normalize.py` — to be created.
- `src/winecollector/services/scraping/parsers.py` — to be created.

### Dependent Files
- `src/winecollector/services/scraping/scraper.py` (task_11) — uses both functions.
- `src/winecollector/services/wine_service.py` (task_13) — uses `normalize_wine_url` for duplicate detection.

### Related ADRs
- [ADR-002: Deduplicação por URL com Incremento Automático de Estoque](adrs/adr-002.md) — defines URL normalization as the duplicate key.
- [ADR-001: Faseamento Arquivista Primeiro](adrs/adr-001.md) — mandates extracting `aging_potential_years` in V1 to avoid a future migration.

## Deliverables
- Two pure functions usable from any layer.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- No integration tests required for this task (pure functions; no integration boundary).

## Tests
- Unit tests:
  - [ ] `tests/unit/test_normalize_url.py::test_lowercases_host` — `normalize_wine_url("https://WWW.WINE.COM.BR/x/prod1.html")` returns `"https://www.wine.com.br/x/prod1.html"`.
  - [ ] `tests/unit/test_normalize_url.py::test_strips_query_and_fragment` — input with `?utm=x#frag` returns the same path without them.
  - [ ] `tests/unit/test_normalize_url.py::test_strips_trailing_slash` — `"https://www.wine.com.br/x/"` returns `"https://www.wine.com.br/x"`.
  - [ ] `tests/unit/test_normalize_url.py::test_rejects_non_wine_com_br_host` — `"https://example.com/x"` raises `ValueError`.
  - [ ] `tests/unit/test_normalize_url.py::test_rejects_non_http_scheme` — `"ftp://www.wine.com.br/x"` raises `ValueError`.
  - [ ] `tests/unit/test_parse_aging_potential.py::test_single_integer_returns_it` — `"5 anos"` → 5.
  - [ ] `tests/unit/test_parse_aging_potential.py::test_range_returns_upper_bound` — `"10 a 15 anos"` → 15.
  - [ ] `tests/unit/test_parse_aging_potential.py::test_ate_n_anos_returns_n` — `"Até 8 anos"` → 8.
  - [ ] `tests/unit/test_parse_aging_potential.py::test_non_numeric_returns_none` — `"Pronto para beber"` → `None`.
  - [ ] `tests/unit/test_parse_aging_potential.py::test_none_input_returns_none` — `None` → `None`.
- Integration tests: not applicable (pure functions).
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- Both functions have no imports from app layers.
- Edge cases enumerated in the TechSpec are all covered.
