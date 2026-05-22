"""Unit tests for the ``WineTasting`` SQLAlchemy model — metadata only."""

from __future__ import annotations

import pytest
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text

from winecollector.database import Base
from winecollector.models import Wine, WineTasting


def test_tasting_is_registered_on_shared_metadata() -> None:
    assert "wine_tastings" in Base.metadata.tables
    assert Base.metadata.tables["wine_tastings"] is WineTasting.__table__


@pytest.mark.parametrize(
    ("col_name", "expected_type", "nullable"),
    [
        ("id", Integer, False),
        ("wine_id", Integer, False),
        ("tasted_at", Date, False),
        ("notes_visual", Text, True),
        ("notes_olfactory", Text, True),
        ("notes_palate", Text, True),
        ("memories", Text, True),
        ("created_at", DateTime, False),
        ("updated_at", DateTime, False),
    ],
)
def test_tasting_columns_match_techspec(
    col_name: str, expected_type: type, nullable: bool
) -> None:
    col = WineTasting.__table__.columns[col_name]
    assert isinstance(
        col.type, expected_type
    ), f"{col_name}: expected {expected_type.__name__}, got {type(col.type).__name__}"
    assert col.nullable is nullable


def test_wine_id_fk_cascades() -> None:
    fks = list(WineTasting.__table__.columns["wine_id"].foreign_keys)
    assert len(fks) == 1
    fk = fks[0]
    assert isinstance(fk, ForeignKey)
    assert fk.column.table.name == "wines"
    assert fk.column.name == "id"
    assert fk.ondelete == "CASCADE"


def test_wine_id_is_indexed() -> None:
    assert WineTasting.__table__.columns["wine_id"].index is True


def test_wine_has_tastings_relationship_with_selectin_loading() -> None:
    rel = Wine.tastings.property
    # back_populates wires both sides; selectin avoids the sync-DB IO trap
    # that would otherwise raise inside async contexts.
    assert rel.lazy == "selectin"
    assert rel.mapper.class_ is WineTasting
    assert rel.back_populates == "wine"
