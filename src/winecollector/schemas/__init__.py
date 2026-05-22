"""Pydantic schemas — request/response contracts decoupled from ORM models."""

from __future__ import annotations

from winecollector.schemas.auth import UserCreate, UserRead
from winecollector.schemas.export import ExportedWine, ExportEnvelope
from winecollector.schemas.tasting import (
    TastingCreate,
    TastingResponse,
    TastingUpdate,
)
from winecollector.schemas.wine import (
    WineCreate,
    WineFilterParams,
    WineResponse,
    WineScrapedData,
    WineUpdate,
)

__all__ = [
    "ExportEnvelope",
    "ExportedWine",
    "TastingCreate",
    "TastingResponse",
    "TastingUpdate",
    "UserCreate",
    "UserRead",
    "WineCreate",
    "WineFilterParams",
    "WineResponse",
    "WineScrapedData",
    "WineUpdate",
]
