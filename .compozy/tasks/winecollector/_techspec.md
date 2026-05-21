# TechSpec: WineCollector

## Executive Summary

WineCollector is delivered as an async Python 3.12 web application: FastAPI + SQLAlchemy 2.0 (async) on top of PostgreSQL 16, with server-rendered Jinja2 templates progressively enhanced by HTMX and Tailwind. Authentication uses `fastapi-users` with a cookie-based JWT transport so HTMX requests carry credentials automatically. The scraper layer uses `httpx.AsyncClient` + BeautifulSoup4 with defensive parsing — every field is optional, every failure is captured as a `scrape_status` value rather than an exception. Wine images are normalized to WebP on download via Pillow and stored on the local filesystem under `data/images/`. The full stack runs locally via Docker Compose and migrates to managed PostgreSQL by changing only `DATABASE_URL`.

The primary trade-off is **simplicity over scale**: ILIKE-based search, no full-text indexes, no pagination in V1, and a single-replica deployment model. This is deliberate — the target is a personal cellar of tens to a few hundred wines, and the engineering surface is kept minimal so that Phase 2 (tasting notebook) and Phase 3 (drinking window) can be added without refactoring the core. The `WineTasting` schema is shipped in V1 (table + model + Pydantic types) with no UI, exactly so that Phase 2 begins with a stable contract.

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Browser (mobile-first)                        │
│              Jinja2 pages + HTMX fragments + Tailwind               │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTP (cookie JWT)
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI application (uvicorn)                    │
│ ┌────────────────────┐   ┌────────────────────┐   ┌──────────────┐  │
│ │ Routers            │──▶│ Services           │──▶│ Models       │  │
│ │ (HTTP only)        │   │ (domain logic)     │   │ (SQLAlchemy) │  │
│ │ • auth.py          │   │ • wine_service     │   │ • Wine       │  │
│ │ • wines.py         │   │ • tasting_service  │   │ • WineTasting│  │
│ │ • exports.py       │   │ • scraper          │   │ • User       │  │
│ │ • pages.py (HTML)  │   │ • export_service   │   │              │  │
│ └────────────────────┘   └─────────┬──────────┘   └──────────────┘  │
│                                    │                                │
│                                    ▼                                │
│                  ┌──────────────────────────────────┐               │
│                  │ Infra adapters                   │               │
│                  │ • httpx scraper client           │               │
│                  │ • Pillow image normalizer        │               │
│                  │ • file storage (data/images/)    │               │
│                  └──────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
           │                              │                  │
           ▼                              ▼                  ▼
   ┌───────────────┐              ┌──────────────┐    ┌─────────────┐
   │ PostgreSQL 16 │              │ wine.com.br  │    │ data/images │
   │ (asyncpg)     │              │ (scraping)   │    │ (filesystem)│
   └───────────────┘              └──────────────┘    └─────────────┘
```

Component responsibilities:

- **Routers** parse HTTP, call services, return `HTMLResponse` (Jinja2 page or fragment) or `JSONResponse` for the JSON export. No SQL.
- **Services** contain the business logic. They receive `AsyncSession` as a parameter and raise domain exceptions (`WineNotFound`, `DuplicateWine`) that routers translate to HTTP errors or HTMX-friendly fragments.
- **Models** are SQLAlchemy 2.0 declarative classes using `Mapped[T]` + `mapped_column()`.
- **Scraper** is a single async module that orchestrates `httpx.AsyncClient` fetch → BeautifulSoup parse → Pillow image normalization → returns a `WineScrapedData` Pydantic object.
- **Templates** live under `src/winecollector/templates/`; partials returned by HTMX are in `templates/partials/`.

The scraper is the only component that talks to the public internet. All other components are local.

## Implementation Design

### Core Interfaces

The scraper contract — every component that triggers scraping depends on this signature, so it is the single most important type to lock down:

```python
# src/winecollector/services/scraper.py
from __future__ import annotations
from pydantic import BaseModel

class WineScrapedData(BaseModel):
    name: str | None = None
    winery: str | None = None
    vintage: int | None = None
    country: str | None = None
    region: str | None = None
    wine_type: str | None = None         # red | white | rose | sparkling | semi_sparkling | fortified
    sweetness: str | None = None         # dry | off_dry | semi_sweet | sweet
    grapes: str | None = None            # free text — preserves original phrasing
    aging: str | None = None             # free text
    alcohol_content: str | None = None   # free text with unit
    serving_temperature: str | None = None
    aging_potential_years: int | None = None
    visual_notes: str | None = None
    olfactory_notes: str | None = None
    palate_notes: str | None = None
    sommelier_notes: str | None = None
    food_pairing: str | None = None
    image_url: str | None = None
    image_path: str | None = None
    scrape_status: str = "failed"        # success | partial | failed

async def scrape_wine(url: str) -> WineScrapedData: ...
```

The wine service contract — duplicate detection + create-or-increment flow:

```python
# src/winecollector/services/wine_service.py
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass
class AddWineOutcome:
    wine_id: int
    was_duplicate: bool   # True if stock was incremented on an existing wine
    new_stock: int

async def add_wine_from_url(
    db: AsyncSession, url: str, *, scraped: WineScrapedData
) -> AddWineOutcome: ...
```

### Data Models

Three tables in V1: `users`, `wines`, `wine_tastings`. The tasting table is created in V1 with no UI consumer per ADR-006.

**`users`** — managed by fastapi-users; standard columns (`id` UUID, `email`, `hashed_password`, `is_active`, `is_superuser`, `is_verified`).

**`wines`** — the catalog row. All column names are in English (per project rule: every non-user-facing identifier is English; Portuguese is reserved for UI labels and the CSV export header):

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `int` | PK | auto |
| `name` | `str` | not null | from scraper or manual |
| `winery` | `str \| None` | nullable | |
| `vintage` | `int \| None` | nullable | vintage year |
| `country` | `str \| None` | nullable | |
| `region` | `str \| None` | nullable | |
| `wine_type` | `str \| None` | nullable, indexed | stored values: `red`, `white`, `rose`, `sparkling`, `semi_sparkling`, `fortified` |
| `sweetness` | `str \| None` | nullable | stored values: `dry`, `off_dry`, `semi_sweet`, `sweet` |
| `grapes` | `str \| None` | nullable | free text — preserves original phrasing |
| `aging` | `str \| None` | nullable | free text |
| `alcohol_content` | `str \| None` | nullable | free text with unit |
| `serving_temperature` | `str \| None` | nullable | free text with unit |
| `aging_potential_years` | `int \| None` | nullable | parsed integer, see scraper |
| `visual_notes` | `text \| None` | nullable | |
| `olfactory_notes` | `text \| None` | nullable | |
| `palate_notes` | `text \| None` | nullable | |
| `sommelier_notes` | `text \| None` | nullable | |
| `food_pairing` | `text \| None` | nullable | |
| `image_url` | `str \| None` | nullable | original URL (traceability + re-scrape) |
| `image_path` | `str \| None` | nullable | relative path `data/images/<uuid>.webp` |
| `source_url` | `str` | not null, unique, indexed | canonical normalized wine.com.br URL — drives duplicate detection |
| `scrape_status` | `str` | not null, default `'manual'` | values: `success`, `partial`, `failed`, `manual` |
| `stock` | `int` | not null, default 1, check ≥ 0 | |
| `purchased_at` | `date` | not null, default today | |
| `created_at` | `timestamptz` | not null, default now | |
| `updated_at` | `timestamptz` | not null, default now, on update now | |

Indexes: `source_url` (unique), `wine_type`, `winery` (for cellar overview ordering), `purchased_at DESC` (default sort).

**Display layer**: a small lookup table in `src/winecollector/i18n/labels.py` maps the stored English values to their Portuguese labels for templates (e.g., `wine_type="red"` → "Tinto"; `sweetness="off_dry"` → "Meio seco"). The mapping is loaded once at import time and used by Jinja2 helpers. This keeps the database canonical and the UI localized without duplicating either.

**`wine_tastings`** — created in V1, queried only via direct SQLAlchemy in tests:

| Column | Type | Constraints |
|---|---|---|
| `id` | `int` | PK |
| `wine_id` | `int` | FK `wines.id` ON DELETE CASCADE, indexed |
| `tasted_at` | `date` | not null, default today |
| `notes_visual` | `text \| None` | nullable |
| `notes_olfactory` | `text \| None` | nullable |
| `notes_palate` | `text \| None` | nullable |
| `memories` | `text \| None` | nullable |
| `created_at` | `timestamptz` | not null, default now |
| `updated_at` | `timestamptz` | not null, default now, on update now |

Pydantic schema layer mirrors the models in `src/winecollector/schemas/`:
- `wine.py`: `WineCreate`, `WineUpdate`, `WineResponse`, `WineFilterParams`, `WineScrapedData`.
- `tasting.py`: `TastingCreate`, `TastingUpdate`, `TastingResponse` (used by tests; no router in V1).
- `auth.py`: `UserRead`, `UserCreate`, `UserUpdate` (fastapi-users defaults extended only if needed).
- `export.py`: `ExportEnvelope` with `schema_version: int = 1`, `exported_at: datetime`, `wines: list[ExportedWine]`.

### API Endpoints

Routes are grouped into HTML routers (return Jinja2 pages and partials) and a JSON exporter route.

| Method | Path | Auth | Description | Response |
|---|---|---|---|---|
| GET | `/signup` | open while users table empty, 404 otherwise | First-run signup form | HTML (Jinja2 page) |
| POST | `/signup` | same gate | Create first user; on success, redirect to `/login` with flash | 303 redirect |
| GET | `/login` | public | Login form | HTML page |
| POST | `/auth/login` | public | fastapi-users login; sets cookie | 204 + Set-Cookie |
| POST | `/auth/logout` | required | Clears cookie | 204 |
| GET | `/` | required | Cellar overview (search + filters + sort) | HTML page |
| GET | `/wines` | required | Cellar overview alias (used by HTMX search) | HTML fragment when `HX-Request` header present, otherwise full page |
| GET | `/wines/new` | required | Add-wine page (URL paste + manual form) | HTML page |
| POST | `/wines/scrape` | required | Trigger scrape for a given URL, returns pre-filled form fragment | HTML fragment (`partials/wine_form.html`) |
| POST | `/wines` | required | Create wine (or increment stock if duplicate URL); redirect to detail | 303 redirect |
| GET | `/wines/{id}` | required | Wine detail page | HTML page |
| POST | `/wines/{id}/stock/increment` | required | +1 stock | HTML fragment (`partials/stock_counter.html`) |
| POST | `/wines/{id}/stock/decrement` | required | -1 stock (no go below 0) | HTML fragment (`partials/stock_counter.html`) |
| GET | `/wines/{id}/edit` | required | Edit form | HTML page |
| POST | `/wines/{id}` | required | Update wine fields | 303 redirect |
| POST | `/wines/{id}/rescrape` | required | Re-fetch original URL or a new URL provided in form | HTML fragment (`partials/wine_detail.html`) |
| POST | `/wines/{id}/delete` | required | Delete wine + image file | 303 redirect to `/` |
| GET | `/export/json` | required | Download `adega.json` | `application/json` with `Content-Disposition` |
| GET | `/export/csv` | required | Download `adega.csv` | `text/csv; charset=utf-8` with `Content-Disposition` |

HTMX-specific behavior:
- Routes returning HTML fragments inspect the `HX-Request` header. When absent (direct browser navigation), they render the full page with the fragment embedded. This means a user can deep-link any URL.
- After `POST /wines/scrape`, the duplicate-detection check runs first; if duplicate, the returned fragment is `partials/duplicate_prompt.html` with the +1 button. Otherwise it's the pre-filled form.

## Integration Points

### wine.com.br (HTTP scraping)

- **Purpose**: fetch wine product pages and download bottle images.
- **Transport**: `httpx.AsyncClient` with `timeout=15s`, `follow_redirects=True`, `verify=True`, descriptive `User-Agent` (`Adega/1.0 (personal wine cellar manager)`).
- **Auth**: none — public pages.
- **Error handling**: every failure path returns a `WineScrapedData(scrape_status="failed")` rather than raising. `httpx.HTTPStatusError`, `httpx.RequestError`, and `asyncio.TimeoutError` are all caught and logged with the URL + status.
- **Retry strategy**: no automatic retries. The user retries explicitly via the "Tentar novamente" button.

### URL normalization (internal canonicalization for duplicate detection)

Applied before insert and before the duplicate-detection `SELECT`. Implemented as a pure function `normalize_wine_url(url: str) -> str`:

1. Strip whitespace.
2. Parse with `urllib.parse.urlsplit`; reject if scheme is not `http`/`https` or netloc does not end with `wine.com.br`.
3. Lowercase the netloc.
4. Drop the query string and fragment entirely (wine.com.br product pages do not need params for identity).
5. Remove trailing slash from the path.
6. Reassemble as `https://www.wine.com.br/<path>`.

Wines with identical normalized URLs are considered the same SKU (per ADR-002).

### Aging-potential parser

`parse_aging_potential(text: str | None) -> int | None` — extracts the integer stored in `Wine.aging_potential_years` from the free-text "Potencial de guarda" field on the source page:

- Return `None` if the input is empty or matches non-numeric patterns ("pronto para beber", "consumir jovem").
- Extract all integers from the string.
- If exactly one integer → return it.
- If two or more → return the maximum (e.g., "10 a 15 anos" → 15; "5-8 anos" → 8).
- If extraction fails → return `None`.

The implementation lives next to the scraper as a pure function for unit testability.

## Impact Analysis

| Component | Impact Type | Description and Risk | Required Action |
|---|---|---|---|
| `src/winecollector/` package | new | Entire application; greenfield | Create the package skeleton (main, config, database, models, schemas, routers, services, templates, static) |
| `pyproject.toml` | new | Dependency manifest | Define FastAPI, SQLAlchemy 2.0, asyncpg, fastapi-users, Pydantic v2, pydantic-settings, httpx, beautifulsoup4, jinja2, python-multipart, Pillow, Alembic, ruff, pytest, pytest-asyncio, pytest-cov, factory-boy |
| `docker-compose.yml` | new | DB + app services | Postgres 16-alpine + app service with healthcheck; volumes for `data/postgres` and `data/images` |
| `Dockerfile` | new | Python 3.12-slim with Poetry | Multi-stage if needed; otherwise single-stage |
| `alembic.ini` + `migrations/env.py` | new | Async-aware Alembic | Initial migrations: `users`, `wines`, `wine_tastings` |
| `.env.example` | new | Env var template | All keys from PRD + IMAGES_DIR + SCRAPER_USER_AGENT + ACCESS_TOKEN_EXPIRE_MINUTES |
| `tests/conftest.py` | new | Fixtures: engine, session, client, factories | Test DB on a separate database; `httpx.AsyncClient + ASGITransport` |
| `.python-version` | new | Pin Python 3.12.x | `3.12.7` |
| `data/images/` | runtime | Image storage directory | Created at app startup if missing |

## Testing Approach

### Unit Tests

Coverage target ≥80% per the testing rule. Each service tested in isolation.

- **`scraper.parse_wine_page`** — exercise with frozen HTML fixtures in `tests/fixtures/html/`:
  - `wine_page_success.html` (all fields present) → `scrape_status = "success"`, every field populated.
  - `wine_page_partial.html` (some fields missing) → `scrape_status = "partial"`, missing fields are `None`.
  - `wine_page_no_image.html` → returns successfully with `image_url = None`.
  - Each test asserts on at least one field's exact value to catch silent parser drift.
- **`scraper.fetch_page`** — mock `httpx.AsyncClient.get` (via `respx` or `pytest-mock`):
  - 200 + valid HTML → returns the body.
  - 404 → returns `None`; logs warning.
  - `httpx.RequestError` (timeout, connection refused) → returns `None`; logs warning.
- **`scraper.parse_aging_potential`** — table-driven:
  - `"5 anos" → 5`
  - `"10 a 15 anos" → 15`
  - `"Até 8 anos" → 8`
  - `"Pronto para beber" → None`
  - `None → None`
- **`scraper.normalize_wine_url`** — table-driven; reject non-`wine.com.br` hosts.
- **`scraper.save_image_as_webp`** — feed a tiny in-memory JPEG and a PNG; assert output is WebP and dimensions are capped at 1600px.
- **`wine_service.add_wine_from_url`** — with real DB session:
  - First add → creates wine, stock = 1, `was_duplicate = False`.
  - Second add same URL → no new wine; stock = 2; `was_duplicate = True`.
- **`export_service.build_envelope`** — assert `schema_version = 1`, sorted by `id`, all fields present.
- **`url_normalizer`** — round-trip and corner cases (uppercase host, trailing slash, query string, fragment).

### Integration Tests

`httpx.AsyncClient` + `ASGITransport` against the full FastAPI app, with a dedicated test database created and dropped per test session.

- **Auth gate**: `/signup` returns 200 when users table is empty, 404 after first user exists.
- **Login flow**: `POST /auth/login` sets the cookie; subsequent `GET /` returns the cellar overview; without cookie returns 401 or redirects.
- **Add wine via URL (mocked scrape)**: monkeypatch `scrape_wine` to return a `WineScrapedData(scrape_status="success", name="Casillero del Diablo", ...)`; assert `POST /wines/scrape` returns the form fragment, `POST /wines` redirects to detail, and the detail page shows the name.
- **Duplicate detection**: add a wine, then `POST /wines/scrape` with the same URL → response is the duplicate prompt fragment; clicking +1 increments stock.
- **Stock controls**: `POST /wines/{id}/stock/increment` and `/decrement` each return a partial; -1 on stock 0 stays at 0.
- **Re-scrape**: monkeypatch `scrape_wine`; `POST /wines/{id}/rescrape` updates fields without changing `source_url` or `stock`.
- **Export JSON**: `GET /export/json` returns content-type `application/json`, parses into `ExportEnvelope`, and the `wines` array length matches the DB.
- **Export CSV**: `GET /export/csv` returns content-type `text/csv`, has the expected Portuguese header row.

Real wine.com.br is **never** hit in tests — all scraping is mocked.

### Language conventions in exports

- **JSON export** (`adega.json`): keys use the English column names from the `wines` table (`name`, `winery`, `vintage`, `wine_type`, `sweetness`, `aging_potential_years`, etc.). The format is a technical contract intended for programmatic re-use; English keys keep it consistent with the rest of the codebase.
- **CSV export** (`adega.csv`): the header row uses Portuguese labels for spreadsheet consumption by the user (`nome,vinícola,safra,uvas,região,tipo,classificação,estoque,data_compra`). The translation happens at the CSV writer; the data layer remains English. Cell values for `wine_type` and `sweetness` are translated to Portuguese (e.g., `red` → "Tinto") via the same display-layer lookup used by templates.

## Development Sequencing

### Build Order

Each step states which previous steps it depends on. A step cannot start until its dependencies are merged.

1. **Project skeleton** — no dependencies. Create `pyproject.toml`, `.python-version`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `alembic.ini`, `src/winecollector/__init__.py`, `src/winecollector/main.py` (empty app), `src/winecollector/config.py` (pydantic-settings).
2. **Database wiring** — depends on step 1. Add `src/winecollector/database.py` with the async engine + `get_session` dependency; verify connection in a smoke test.
3. **User model + auth backend** — depends on step 2. Add `User` model, fastapi-users setup with `CookieTransport` + `JWTStrategy`, ADR-005 first-run signup route, `/login`, `/auth/login`, `/auth/logout` routes, `templates/auth/login.html`, `templates/auth/signup.html`, `templates/base.html`.
4. **Initial Alembic migrations** — depends on step 3. Generate the `users` table migration; apply via `alembic upgrade head`.
5. **Wine model + migration** — depends on step 4. Add `Wine` SQLAlchemy model with every field from the data-model table; generate migration; apply.
6. **WineTasting model + migration** — depends on step 5. Add `WineTasting` model per ADR-006; generate migration; apply. No UI.
7. **Pydantic schemas** — depends on step 5 (and 6 for tasting). Add `schemas/wine.py`, `schemas/tasting.py`, `schemas/export.py`.
8. **URL normalizer + aging-potential parser** — depends on step 1 only (pure functions). Add `src/winecollector/services/scraping/normalize.py` and `parsers.py`; unit-test exhaustively.
9. **Scraper service** — depends on steps 5, 7, 8. Implement `scrape_wine(url)` returning `WineScrapedData`. Use frozen HTML fixtures in `tests/fixtures/html/`.
10. **Image normalizer (Pillow → WebP)** — depends on step 1. Pure function `save_image_as_webp(content, dest_dir) -> Path`. Unit-tested.
11. **Wine service** — depends on steps 5, 7, 8, 9. `add_wine_from_url`, `update_wine`, `delete_wine`, `increment_stock`, `decrement_stock`, `list_wines(filters)` with ILIKE search.
12. **Wine routers + templates** — depends on steps 3, 11. `routers/wines.py` and `routers/pages.py`; `templates/wines/{index,detail,form}.html`; `templates/partials/{wine_card,wine_form,duplicate_prompt,stock_counter,wine_detail,scrape_result}.html`.
13. **Export service + routes** — depends on step 11. JSON envelope with `schema_version=1`; CSV with PT-BR header row.
14. **Static assets** — depends on step 3. Tailwind via CDN Play in `base.html`; HTMX via CDN; `static/css/app.css` for any minimal overrides.
15. **End-to-end integration tests** — depends on steps 12, 13. Exercise the full happy path + duplicate + failed scrape.

### Technical Dependencies

- Python 3.12.x installed via pyenv.
- Docker Desktop or Docker Engine for the Postgres container.
- Outbound HTTPS access to wine.com.br for live testing (tests themselves never hit it).
- `openssl` available to generate the JWT `SECRET_KEY` for `.env`.

No external service accounts, no API keys, no third-party APIs.

## Monitoring and Observability

V1 is single-user, locally deployed — full observability tooling is overkill. The minimum:

- **Structured logging** via Python's stdlib `logging`, configured in `main.py` to JSON in production (`ENVIRONMENT=production`) and human-readable in development.
- **Scrape failure logs** — every scrape failure logged at WARNING with fields `url`, `http_status` (when applicable), `exc_type`, `scrape_status`. No headers, no cookies.
- **Auth events** — login success/failure logged at INFO with the user email (the only PII in scope, and the user owns the logs).
- **Request access log** — uvicorn's access log is sufficient.
- **Health endpoint** — `GET /health` returns `{"status": "ok", "db": "ok"}` after `SELECT 1`. Used by Docker healthcheck.

No metrics collector, no tracing, no alerting in V1. If the user later self-hosts on a managed platform, adding a Prometheus exporter is a small additive change.

## Technical Considerations

### Key Decisions

- **Cookie-based JWT (ADR-004)** — Decision: `CookieTransport` only. Rationale: zero-JS auth for HTMX. Trade-off: a future `/api` will need a second backend. Alternatives rejected: Bearer (requires JS), both transports (YAGNI).
- **First-run signup screen (ADR-005)** — Decision: `/signup` open until users table is non-empty, then 404. Rationale: zero-CLI first-run UX without leaving a permanent registration surface. Trade-off: ~10 lines of code for the gate logic. Alternatives rejected: CLI script (friction), permanent signup (security smell), env-var seeding (plaintext password).
- **WineTasting table in V1 (ADR-006)** — Decision: ship the schema, defer the UI. Rationale: avoid a Phase-2 schema rush. Trade-off: a few unused model files. Alternatives rejected: pure YAGNI (risky), JSONB column (limits future queries).
- **ILIKE search (ADR-007)** — Decision: substring matching, no indexes. Rationale: data volume tiny. Trade-off: no stemming, no typo tolerance. Alternatives rejected: tsvector (overkill), pg_trgm (deferred).
- **WebP image conversion (ADR-008)** — Decision: Pillow normalizes every image to WebP at download. Rationale: uniform on-disk format, smaller files. Trade-off: extra dependency + small CPU cost. Alternatives rejected: preserve original (heterogeneous), lazy conversion (over-engineered).
- **`source_url` as duplicate key (ADR-002)** — Decision: enforce unique constraint on the normalized URL. Trade-off: same URL with a future vintage change is treated as the same wine; the user can edit the `vintage` field manually.

### Known Risks

- **wine.com.br DOM changes break the parser.** Likelihood: medium over a 12-month horizon. Mitigation: defensive parsing — every field is optional, parser logs warnings for missing fields, partial scrapes still produce a usable wine row; integration tests use frozen fixtures so we catch parser regressions immediately.
- **Pillow image-bomb DoS.** Likelihood: very low (source is wine.com.br, not user uploads). Mitigation: `PIL.Image.MAX_IMAGE_PIXELS` set to a sane limit; download size capped via httpx (`max_redirects`, response-size guard).
- **JWT secret leakage via `.env` commit.** Mitigation: `.env` in `.gitignore` from the first commit; `.env.example` carries the placeholder only.
- **Migration drift between dev and prod.** Mitigation: `alembic upgrade head` runs at container startup (in `docker-compose` and any future cloud deploy); fail-fast if migrations cannot apply.
- **Cellar grows past ILIKE's comfortable range.** Mitigation: revisit when scans cross 200ms; adding a `pg_trgm` GIN index is purely additive.

## Architecture Decision Records

- [ADR-001: Faseamento "Arquivista Primeiro"](adrs/adr-001.md) — Three-phase rollout: catalog/scraping in V1, tastings in Phase 2, drinking window in Phase 3.
- [ADR-002: Deduplicação por URL com Incremento Automático de Estoque](adrs/adr-002.md) — Normalized `source_url` is the SKU key; repeat cadastro increments stock instead of creating duplicates.
- [ADR-003: Exportação JSON/CSV Manual no MVP](adrs/adr-003.md) — In-app JSON/CSV export honors the "you own your data" positioning alongside infra-level rclone backups.
- [ADR-004: Cookie-Based JWT Transport for HTMX/Jinja2 UI](adrs/adr-004.md) — `fastapi-users` `CookieTransport` so HTMX requests carry auth without JavaScript.
- [ADR-005: First-Run Signup Screen with Self-Closing Registration](adrs/adr-005.md) — `/signup` open while the users table is empty, then 404 — no CLI, no permanent registration surface.
- [ADR-006: WineTasting Schema Created in V1, UI Deferred to Phase 2](adrs/adr-006.md) — Ship the table + model + schemas in V1 so Phase 2 begins with a stable contract.
- [ADR-007: ILIKE-Based Search in MVP (No Full-Text Index)](adrs/adr-007.md) — Substring matching with `OR` across `name`, `winery`, `region`; no PG extensions; revisit if scale changes.
- [ADR-008: Convert Wine Images to WebP via Pillow on Download](adrs/adr-008.md) — Uniform on-disk WebP format, quality 85, max 1600px on the longer edge, conversion off the event loop via `asyncio.to_thread`.
