<!-- Scope: **/*.py — Python coding standards, async patterns, FastAPI and SQLAlchemy 2.0 -->

# Python Coding Standards

## Style & Formatting
- Follow **PEP 8**; use `ruff` for linting and formatting
- Max line length: **88 characters**
- Use **double quotes** for strings
- Use **trailing commas** in multi-line collections
- Run `ruff check . --fix && ruff format .` before committing

## Type Hints
- **Always** add type hints to all function parameters and return values
- Use `from __future__ import annotations` at the top of every file
- Use built-in generics: `list[str]`, `dict[str, int]`, `tuple[int, ...]`
- Use `X | None` instead of `Optional[X]`
- Use `X | Y` instead of `Union[X, Y]`

```python
# ✅ Good
from __future__ import annotations

async def get_wine(wine_id: int, db: AsyncSession) -> Wine | None:
    ...

# ❌ Avoid
from typing import Optional
async def get_wine(wine_id: int, db: AsyncSession) -> Optional[Wine]:
    ...
```

## Async Code (critical — this project is fully async)
- All DB calls use `async with`, `await session.execute(...)` — never sync SQLAlchemy calls
- All HTTP calls (scraping) use `async with httpx.AsyncClient()`
- Use `asyncio.gather()` for concurrent operations, not sequential `await`s in a loop
- Never call `asyncio.run()` inside a running event loop

```python
# ✅ Good
async def scrape_wine(url: str) -> WineScrapedData:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
    ...

# ❌ Never — sync requests inside async handler
def scrape_wine(url: str) -> WineScrapedData:
    response = requests.get(url)
    ...
```

## FastAPI Patterns
- **Routers** handle HTTP only: validate input, call a service function, return the response
- **Services** contain all business logic; they receive an `AsyncSession` as a parameter
- **Never** put SQL queries directly in routers
- Use `Annotated` for dependency injection (FastAPI's recommended style)

```python
# ✅ Good — router delegates to service
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from adega.database import get_session
from adega.services import wine_service

router = APIRouter(prefix="/wines", tags=["wines"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.get("/{wine_id}")
async def get_wine(wine_id: int, db: SessionDep) -> WineResponse:
    wine = await wine_service.get_by_id(db, wine_id)
    if wine is None:
        raise HTTPException(status_code=404, detail="Wine not found")
    return wine
```

## SQLAlchemy 2.0 Patterns
- Use declarative base with `DeclarativeBase`
- Always define `__tablename__` explicitly
- Use `Mapped[T]` and `mapped_column()` for column definitions (new 2.0 syntax)
- Use `relationship()` with `lazy="selectin"` for async compatibility

```python
# ✅ Good — SQLAlchemy 2.0 declarative style
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Date
import datetime

class Base(DeclarativeBase):
    pass

class Wine(Base):
    __tablename__ = "wines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    vintage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    purchased_at: Mapped[datetime.date] = mapped_column(Date, nullable=False)
```

## Pydantic v2 Schemas
- Keep Pydantic schemas in `schemas/` separate from SQLAlchemy models in `models/`
- Use `model_config = ConfigDict(from_attributes=True)` on response schemas
- Name schemas as `WineCreate`, `WineUpdate`, `WineResponse` for clarity

## Functions & Classes
- Use **early returns** to avoid deep nesting
- Keep functions focused on a single responsibility
- Add **docstrings** to all public service functions (Google style)
- Prefer `dataclasses` or Pydantic models over plain dicts for structured data

## Error Handling
- Catch specific exceptions; never use bare `except:`
- In services, raise domain exceptions; let routers convert them to HTTP errors
- Always log exceptions with context using `logger.exception()`

```python
# ✅ Good
try:
    data = await scrape_wine(url)
except httpx.HTTPStatusError as exc:
    logger.exception("Scraping failed for URL %s: %s", url, exc)
    raise ScrapingError(f"Could not scrape {url}") from exc
```

## Imports Order (enforced by ruff/isort)
1. `from __future__ import annotations`
2. Standard library
3. Third-party (fastapi, sqlalchemy, pydantic, httpx…)
4. Local project (`adega.*`)
