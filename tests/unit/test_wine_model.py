"""Unit tests for the ``Wine`` SQLAlchemy model.

Pure metadata assertions — no database connection. Integration coverage
(real inserts, unique constraint, CHECK constraint) lives in
``tests/integration/test_wines_migration.py``.
"""

from __future__ import annotations

import pytest
from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String, Text

from winecollector.database import Base
from winecollector.models import Wine


def test_wine_is_registered_on_shared_metadata() -> None:
    assert "wines" in Base.metadata.tables
    assert Base.metadata.tables["wines"] is Wine.__table__


@pytest.mark.parametrize(
    ("col_name", "expected_type", "nullable"),
    [
        ("id", Integer, False),
        ("name", String, False),
        ("winery", String, True),
        ("vintage", Integer, True),
        ("country", String, True),
        ("region", String, True),
        ("wine_type", String, True),
        ("sweetness", String, True),
        ("grapes", String, True),
        ("aging", String, True),
        ("alcohol_content", String, True),
        ("serving_temperature", String, True),
        ("aging_potential_years", Integer, True),
        ("visual_notes", Text, True),
        ("olfactory_notes", Text, True),
        ("palate_notes", Text, True),
        ("sommelier_notes", Text, True),
        ("food_pairing", Text, True),
        ("image_url", String, True),
        ("image_path", String, True),
        ("source_url", String, False),
        ("scrape_status", String, False),
        ("stock", Integer, False),
        ("purchased_at", Date, False),
        ("created_at", DateTime, False),
        ("updated_at", DateTime, False),
    ],
)
def test_wine_columns_match_techspec(
    col_name: str, expected_type: type, nullable: bool
) -> None:
    col = Wine.__table__.columns[col_name]
    assert isinstance(
        col.type, expected_type
    ), f"{col_name}: expected {expected_type.__name__}, got {type(col.type).__name__}"
    assert col.nullable is nullable


def test_source_url_is_unique_and_indexed() -> None:
    col = Wine.__table__.columns["source_url"]
    assert col.unique is True
    assert col.index is True
    assert col.nullable is False


@pytest.mark.parametrize("col_name", ["wine_type", "winery", "purchased_at"])
def test_secondary_indexes_are_present(col_name: str) -> None:
    col = Wine.__table__.columns[col_name]
    assert col.index is True, f"{col_name} should be indexed"


def test_stock_has_check_constraint_non_negative() -> None:
    check_constraints = [
        c
        for c in Wine.__table__.constraints
        if isinstance(c, CheckConstraint) and c.name == "ck_wines_stock_non_negative"
    ]
    assert (
        len(check_constraints) == 1
    ), "expected exactly one CHECK constraint named ck_wines_stock_non_negative"


def test_stock_defaults_to_one() -> None:
    col = Wine.__table__.columns["stock"]
    default = col.server_default
    assert default is not None
    assert getattr(default, "arg", str(default.arg)) == "1" or "1" in str(default.arg)


def test_scrape_status_defaults_to_manual() -> None:
    col = Wine.__table__.columns["scrape_status"]
    default = col.server_default
    assert default is not None
    rendered = default.arg if isinstance(default.arg, str) else str(default.arg)
    assert rendered == "manual"


def test_updated_at_has_onupdate_clause() -> None:
    col = Wine.__table__.columns["updated_at"]
    assert col.onupdate is not None
    assert col.server_default is not None


def test_id_is_primary_key_and_autoincrement() -> None:
    col = Wine.__table__.columns["id"]
    assert col.primary_key is True
    assert col.autoincrement is True
