"""Schema ↔ ORM round-trip checks.

Insert a real ``Wine`` (plus a child ``WineTasting``) into an in-memory
SQLite database, then validate it back through ``WineResponse`` and
``ExportedWine``. Catches any field-name drift between the model and the
Pydantic shape.
"""

from __future__ import annotations

import datetime
from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from winecollector.database import Base
from winecollector.models import Wine, WineTasting
from winecollector.schemas.export import ExportedWine
from winecollector.schemas.wine import WineResponse


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as s:
            yield s
    finally:
        await engine.dispose()


async def test_wine_response_from_orm_instance(session: AsyncSession) -> None:
    wine = Wine(
        name="Casillero del Diablo",
        winery="Concha y Toro",
        vintage=2020,
        country="Chile",
        region="Valle Central",
        wine_type="red",
        sweetness="dry",
        grapes="Cabernet Sauvignon",
        aging="6 meses em carvalho",
        alcohol_content="13.5%",
        serving_temperature="16-18°C",
        aging_potential_years=5,
        visual_notes="Rubi escuro",
        olfactory_notes="Frutas vermelhas e baunilha",
        palate_notes="Encorpado, taninos sedosos",
        sommelier_notes="Ótimo custo-benefício",
        food_pairing="Carnes vermelhas, queijos curados",
        image_url="https://wine.com.br/img.jpg",
        image_path="data/images/uuid.webp",
        source_url="https://wine.com.br/casillero",
        scrape_status="success",
        stock=3,
        purchased_at=datetime.date(2026, 5, 22),
    )
    session.add(wine)
    await session.commit()
    await session.refresh(wine)

    response = WineResponse.model_validate(wine)

    assert response.id == wine.id
    assert response.name == "Casillero del Diablo"
    assert response.winery == "Concha y Toro"
    assert response.vintage == 2020
    assert response.wine_type == "red"
    assert response.sweetness == "dry"
    assert response.source_url == "https://wine.com.br/casillero"
    assert response.stock == 3
    assert response.purchased_at == datetime.date(2026, 5, 22)
    assert response.created_at is not None
    assert response.updated_at is not None


async def test_exported_wine_includes_tastings(session: AsyncSession) -> None:
    wine = Wine(name="With tasting", source_url="https://wine.com.br/wt")
    session.add(wine)
    await session.flush()
    session.add(
        WineTasting(
            wine_id=wine.id,
            memories="Aniversário de casamento.",
            notes_palate="Equilibrado",
        )
    )
    await session.commit()

    fetched = (
        await session.execute(select(Wine).where(Wine.id == wine.id))
    ).scalar_one()
    await session.refresh(fetched, attribute_names=["tastings"])

    exported = ExportedWine.model_validate(fetched)
    assert exported.source_url == "https://wine.com.br/wt"
    assert len(exported.tastings) == 1
    assert exported.tastings[0].memories == "Aniversário de casamento."
