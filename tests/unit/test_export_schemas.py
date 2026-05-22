"""Unit tests for the export envelope schema (ADR-003)."""

from __future__ import annotations

import datetime

from winecollector.schemas.export import ExportedWine, ExportEnvelope


def test_export_envelope_default_schema_version_is_1() -> None:
    envelope = ExportEnvelope()
    assert envelope.schema_version == 1
    assert envelope.wines == []
    assert isinstance(envelope.exported_at, datetime.datetime)
    # exported_at default is timezone-aware UTC so old/new exports compare
    # cleanly across DST boundaries.
    assert envelope.exported_at.tzinfo is not None


def test_export_envelope_serializes_wines() -> None:
    wine = ExportedWine(
        id=1,
        name="Casillero",
        source_url="https://wine.com.br/prod1",
        scrape_status="manual",
        stock=2,
        purchased_at=datetime.date(2026, 5, 22),
        created_at=datetime.datetime(2026, 5, 22, 10, 0, tzinfo=datetime.UTC),
        updated_at=datetime.datetime(2026, 5, 22, 10, 0, tzinfo=datetime.UTC),
    )
    envelope = ExportEnvelope(wines=[wine])

    payload = envelope.model_dump(mode="json")
    assert payload["schema_version"] == 1
    assert len(payload["wines"]) == 1
    assert payload["wines"][0]["source_url"] == "https://wine.com.br/prod1"
    # ``tastings`` is included as an empty list for new wines.
    assert payload["wines"][0]["tastings"] == []
