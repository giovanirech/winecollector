"""Pydantic schemas for the ``WineTasting`` resource.

Shipped in V1 per ADR-006 but with no router consumer yet — Phase 2 wires
these into the tasting notebook UI. The shape mirrors the ORM model so
Phase 2 can validate against a stable contract.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class TastingCreate(BaseModel):
    """Payload to record a new tasting entry against a specific wine."""

    wine_id: int
    tasted_at: datetime.date | None = None
    notes_visual: str | None = None
    notes_olfactory: str | None = None
    notes_palate: str | None = None
    memories: str | None = None


class TastingUpdate(BaseModel):
    """Partial edit — every field optional."""

    tasted_at: datetime.date | None = None
    notes_visual: str | None = None
    notes_olfactory: str | None = None
    notes_palate: str | None = None
    memories: str | None = None


class TastingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wine_id: int
    tasted_at: datetime.date
    notes_visual: str | None = None
    notes_olfactory: str | None = None
    notes_palate: str | None = None
    memories: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
