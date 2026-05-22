"""Pydantic schemas for the ``Wine`` resource.

Five contracts:

- :class:`WineScrapedData` — scraper output (TechSpec "Core Interfaces").
- :class:`WineCreate` — manual / scrape-confirmed cadastro payload.
- :class:`WineUpdate` — partial edit (every field optional).
- :class:`WineResponse` — ORM ↔ HTTP shape (``from_attributes=True``).
- :class:`WineFilterParams` — cellar query filters.

All identifiers stay English; UI strings (templates, CSV header) handle
Portuguese separately (TechSpec "Display layer").
"""

from __future__ import annotations

import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

WineType = Literal["red", "white", "rose", "sparkling", "semi_sparkling", "fortified"]
Sweetness = Literal["dry", "off_dry", "semi_sweet", "sweet"]
ScrapeStatus = Literal["success", "partial", "failed", "manual"]
SortKey = Literal["purchased_at", "name", "winery", "vintage"]


class WineScrapedData(BaseModel):
    """Defensive payload returned by the scraper — every field optional so
    parse failures degrade gracefully (``scrape_status='partial'`` /
    ``'failed'``) instead of raising."""

    name: str | None = None
    winery: str | None = None
    vintage: int | None = None
    country: str | None = None
    region: str | None = None
    wine_type: str | None = None
    sweetness: str | None = None
    grapes: str | None = None
    aging: str | None = None
    alcohol_content: str | None = None
    serving_temperature: str | None = None
    aging_potential_years: int | None = None
    visual_notes: str | None = None
    olfactory_notes: str | None = None
    palate_notes: str | None = None
    sommelier_notes: str | None = None
    food_pairing: str | None = None
    image_url: str | None = None
    image_path: str | None = None
    scrape_status: ScrapeStatus = "failed"


class WineCreate(BaseModel):
    """User-supplied or scrape-confirmed payload that becomes a new
    ``Wine`` row. ``source_url`` is required because duplicate detection
    (ADR-002) keys off it."""

    name: str
    source_url: str
    winery: str | None = None
    vintage: int | None = None
    country: str | None = None
    region: str | None = None
    wine_type: WineType | None = None
    sweetness: Sweetness | None = None
    grapes: str | None = None
    aging: str | None = None
    alcohol_content: str | None = None
    serving_temperature: str | None = None
    aging_potential_years: int | None = None
    visual_notes: str | None = None
    olfactory_notes: str | None = None
    palate_notes: str | None = None
    sommelier_notes: str | None = None
    food_pairing: str | None = None
    image_url: str | None = None
    image_path: str | None = None
    scrape_status: ScrapeStatus = "manual"
    stock: int = Field(default=1, ge=0)
    purchased_at: datetime.date | None = None


class WineUpdate(BaseModel):
    """Partial-edit payload. Every field is optional so callers can patch
    a single attribute without sending the rest."""

    name: str | None = None
    winery: str | None = None
    vintage: int | None = None
    country: str | None = None
    region: str | None = None
    wine_type: WineType | None = None
    sweetness: Sweetness | None = None
    grapes: str | None = None
    aging: str | None = None
    alcohol_content: str | None = None
    serving_temperature: str | None = None
    aging_potential_years: int | None = None
    visual_notes: str | None = None
    olfactory_notes: str | None = None
    palate_notes: str | None = None
    sommelier_notes: str | None = None
    food_pairing: str | None = None
    image_url: str | None = None
    image_path: str | None = None
    scrape_status: ScrapeStatus | None = None
    stock: int | None = Field(default=None, ge=0)
    purchased_at: datetime.date | None = None


class WineResponse(BaseModel):
    """ORM-friendly response shape — ``from_attributes=True`` lets
    ``WineResponse.model_validate(wine)`` consume a SQLAlchemy ``Wine``
    instance directly."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    winery: str | None = None
    vintage: int | None = None
    country: str | None = None
    region: str | None = None
    wine_type: str | None = None
    sweetness: str | None = None
    grapes: str | None = None
    aging: str | None = None
    alcohol_content: str | None = None
    serving_temperature: str | None = None
    aging_potential_years: int | None = None
    visual_notes: str | None = None
    olfactory_notes: str | None = None
    palate_notes: str | None = None
    sommelier_notes: str | None = None
    food_pairing: str | None = None
    image_url: str | None = None
    image_path: str | None = None
    source_url: str
    scrape_status: str
    stock: int
    purchased_at: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime


class WineFilterParams(BaseModel):
    """Cellar overview query filters (TechSpec "API Endpoints" — search
    + filters + sort). Every field is optional; an empty instance means
    "no filtering"."""

    q: str | None = None
    wine_type: WineType | None = None
    sweetness: Sweetness | None = None
    in_stock: bool | None = None
    sort: SortKey = "purchased_at"
