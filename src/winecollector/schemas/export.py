"""Export envelope for ``GET /export/json`` (ADR-003).

A versioned wrapper — ``schema_version`` lets future importers/migrators
detect old exports without parsing the body. Bump the version whenever
the on-disk shape changes incompatibly.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field

from winecollector.schemas.tasting import TastingResponse
from winecollector.schemas.wine import WineResponse


class ExportedWine(WineResponse):
    """A wine row with its tasting history embedded — ``WineResponse``
    fields are inherited; the only addition is the ``tastings`` list."""

    model_config = ConfigDict(from_attributes=True)

    tastings: list[TastingResponse] = Field(default_factory=list)


class ExportEnvelope(BaseModel):
    """Top-level structure of ``adega.json`` (ADR-003)."""

    schema_version: int = 1
    exported_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    wines: list[ExportedWine] = Field(default_factory=list)
