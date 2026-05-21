<!-- Always active — project overview, stack, structure, and general conventions -->

# Adega Pessoal — Project Overview

## Purpose
Personal wine cellar manager. Allows the user to save information about purchased wines (grapes, vintage, region, winery, aging, aging potential, organoleptic characteristics, stock quantity, and tasting memories). Wine data and images are collected automatically via web scraping from wine.com.br, with manual input as a fallback. Designed as a personal tool but built to be open-source and potentially multi-user.

## Tech Stack
- **Language:** Python 3.12+
- **Package Manager:** Poetry
- **Python Version Manager:** pyenv
- **Web Framework:** FastAPI (async)
- **ORM:** SQLAlchemy 2.0 (declarative, async)
- **Migrations:** Alembic
- **Auth:** fastapi-users (username/password + JWT)
- **Validation:** Pydantic v2
- **Template Engine:** Jinja2
- **CSS:** Tailwind CSS
- **Frontend Interactivity:** HTMX
- **Scraping:** httpx + BeautifulSoup4
- **Database:** PostgreSQL 16 (local via Docker Compose)
- **Async DB Driver:** asyncpg
- **Image Storage:** Local filesystem at `./data/images/`, path saved in DB
- **Backup:** rclone (sync to Google Drive)
- **Containerization:** Docker Compose

## Directory Structure
```
adega/
├── src/
│   └── adega/
│       ├── main.py                # FastAPI app factory
│       ├── config.py              # Settings via pydantic-settings
│       ├── database.py            # SQLAlchemy async engine + session
│       ├── models/                # SQLAlchemy declarative models
│       │   ├── wine.py
│       │   └── tasting.py
│       ├── schemas/               # Pydantic v2 schemas (request/response)
│       │   ├── wine.py
│       │   └── tasting.py
│       ├── routers/               # FastAPI routers (one per domain)
│       │   ├── wines.py
│       │   ├── tastings.py
│       │   └── auth.py
│       ├── services/              # Business logic layer
│       │   ├── wine_service.py
│       │   └── scraper.py         # wine.com.br scraping logic
│       ├── templates/             # Jinja2 HTML templates
│       │   ├── base.html
│       │   ├── wines/
│       │   └── tastings/
│       └── static/                # CSS, JS, images served by FastAPI
│           ├── css/
│           └── js/
├── data/
│   ├── images/                    # Wine bottle images (scraped)
│   └── postgres/                  # Postgres data volume (Docker)
├── migrations/                    # Alembic migration files
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── scripts/                       # Utility scripts (backup, seed, etc.)
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

## Domain Model (key entities)
- **Wine** — core entity; holds all wine metadata, image path, source URL, scrape status, stock quantity, and purchase date
- **WineTasting** — degustação notes linked to a wine; includes `tasted_at`, `notes` (organoleptic observations), and `memories` (personal narrative about the occasion)
- **User** — managed by fastapi-users; single user for now, multi-user ready

## Scraping Strategy
- Scraping is **on-demand only** (triggered when adding a wine or manually refreshing a specific wine)
- Target: wine.com.br product pages
- If scraping fails, `scrape_status` is set to `"failed"` and the UI shows a warning allowing manual input
- User can re-trigger scraping at any time with the original URL or a new one

## General Conventions
- All async code uses `async/await`; no sync DB calls in request handlers
- Business logic lives in `services/`, not in routers
- Routers handle HTTP only: parse input, call service, return response
- Templates use HTMX for dynamic interactions (no custom JavaScript unless unavoidable)
- All environment variables loaded via `pydantic-settings` from `.env`
- Never commit `.env`; keep `.env.example` updated
