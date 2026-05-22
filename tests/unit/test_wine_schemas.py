"""Unit tests for the wine-resource Pydantic schemas."""

from __future__ import annotations

import datetime

import pytest
from pydantic import ValidationError

from winecollector.schemas.wine import (
    WineCreate,
    WineFilterParams,
    WineScrapedData,
    WineUpdate,
)


def test_wine_scraped_data_defaults_all_optional() -> None:
    """Every field optional — only ``scrape_status`` carries a default,
    which mirrors the TechSpec "Core Interfaces" contract."""
    payload = WineScrapedData()

    assert payload.scrape_status == "failed"
    assert payload.name is None
    assert payload.winery is None
    assert payload.vintage is None
    assert payload.image_url is None


def test_wine_scraped_data_accepts_full_payload() -> None:
    payload = WineScrapedData(
        name="Casillero",
        winery="Concha y Toro",
        vintage=2020,
        scrape_status="success",
    )

    assert payload.name == "Casillero"
    assert payload.vintage == 2020
    assert payload.scrape_status == "success"


@pytest.mark.parametrize("missing", ["name", "source_url"])
def test_wine_create_requires_name_and_source_url(missing: str) -> None:
    data: dict[str, object] = {
        "name": "Casillero",
        "source_url": "https://wine.com.br/prod1",
    }
    del data[missing]

    with pytest.raises(ValidationError) as exc_info:
        WineCreate(**data)  # type: ignore[arg-type]
    assert missing in str(exc_info.value)


def test_wine_create_rejects_negative_stock() -> None:
    with pytest.raises(ValidationError):
        WineCreate(
            name="Negative",
            source_url="https://wine.com.br/neg",
            stock=-1,
        )


def test_wine_create_rejects_invalid_wine_type_enum() -> None:
    with pytest.raises(ValidationError):
        WineCreate(
            name="X",
            source_url="https://wine.com.br/x",
            wine_type="purple",  # type: ignore[arg-type]
        )


def test_wine_update_allows_empty_payload() -> None:
    # Every field optional — patching nothing is valid.
    WineUpdate()


def test_wine_filter_params_accepts_empty() -> None:
    params = WineFilterParams()
    assert params.q is None
    assert params.wine_type is None
    assert params.sort == "purchased_at"


def test_wine_filter_params_parses_query_string() -> None:
    params = WineFilterParams(
        q="malbec",
        wine_type="red",
        sweetness="dry",
        in_stock=True,
        sort="name",
    )
    assert params.q == "malbec"
    assert params.wine_type == "red"
    assert params.sweetness == "dry"
    assert params.in_stock is True
    assert params.sort == "name"


def test_wine_filter_params_rejects_unknown_sort_key() -> None:
    with pytest.raises(ValidationError):
        WineFilterParams(sort="random")  # type: ignore[arg-type]


def test_wine_create_default_scrape_status_is_manual() -> None:
    """Manually-entered wines default to ``scrape_status='manual'``."""
    wine = WineCreate(name="Manual", source_url="https://wine.com.br/manual")
    assert wine.scrape_status == "manual"
    assert wine.stock == 1


def test_wine_create_accepts_purchased_at_date() -> None:
    today = datetime.date(2026, 5, 22)
    wine = WineCreate(
        name="With date",
        source_url="https://wine.com.br/d",
        purchased_at=today,
    )
    assert wine.purchased_at == today
