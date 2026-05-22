"""Unit tests for the tasting Pydantic schemas."""

from __future__ import annotations

import datetime

import pytest
from pydantic import ValidationError

from winecollector.schemas.tasting import (
    TastingCreate,
    TastingResponse,
    TastingUpdate,
)


def test_tasting_create_requires_wine_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        TastingCreate()  # type: ignore[call-arg]
    assert "wine_id" in str(exc_info.value)


def test_tasting_create_accepts_minimum_payload() -> None:
    tasting = TastingCreate(wine_id=1)
    assert tasting.wine_id == 1
    assert tasting.notes_visual is None
    assert tasting.memories is None


def test_tasting_create_accepts_full_payload() -> None:
    tasting = TastingCreate(
        wine_id=42,
        tasted_at=datetime.date(2026, 5, 22),
        notes_visual="Rubi denso",
        memories="Jantar de família.",
    )
    assert tasting.wine_id == 42
    assert tasting.notes_visual == "Rubi denso"


def test_tasting_update_allows_empty_payload() -> None:
    TastingUpdate()


def test_tasting_response_has_from_attributes_config() -> None:
    assert TastingResponse.model_config.get("from_attributes") is True
