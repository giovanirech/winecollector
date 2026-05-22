"""Integration tests for the ``wine_tastings`` table — FK cascade + defaults.

SQLite respects ``ON DELETE CASCADE`` only when ``PRAGMA foreign_keys`` is
turned on per connection. The fixture registers a ``connect`` listener
that flips it on for the lifetime of the engine, matching Postgres's
default behavior closely enough for the cascade semantics we are checking.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from winecollector.database import Base
from winecollector.models import Wine, WineTasting


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as s:
            yield s
    finally:
        await engine.dispose()


async def test_insert_and_select_tasting(session: AsyncSession) -> None:
    wine = Wine(name="Casillero", source_url="https://wine.com.br/casillero")
    session.add(wine)
    await session.flush()

    tasting = WineTasting(
        wine_id=wine.id,
        notes_visual="Rubi intenso",
        notes_olfactory="Frutas vermelhas",
        memories="Jantar com amigos no inverno.",
    )
    session.add(tasting)
    await session.commit()

    fetched = (
        await session.execute(select(WineTasting).where(WineTasting.id == tasting.id))
    ).scalar_one()
    assert fetched.wine_id == wine.id
    assert fetched.memories == "Jantar com amigos no inverno."
    # server default populated
    assert fetched.tasted_at is not None


async def test_delete_wine_cascades_to_tastings(session: AsyncSession) -> None:
    wine = Wine(name="Cascade Target", source_url="https://wine.com.br/cascade")
    session.add(wine)
    await session.flush()
    session.add_all(
        [
            WineTasting(wine_id=wine.id, memories="Primeira garrafa."),
            WineTasting(wine_id=wine.id, memories="Segunda garrafa."),
        ]
    )
    await session.commit()

    count_before = (
        (
            await session.execute(
                select(WineTasting).where(WineTasting.wine_id == wine.id)
            )
        )
        .scalars()
        .all()
    )
    assert len(count_before) == 2

    await session.delete(wine)
    await session.commit()

    count_after = (
        (
            await session.execute(
                select(WineTasting).where(WineTasting.wine_id == wine.id)
            )
        )
        .scalars()
        .all()
    )
    assert count_after == []


async def test_new_wine_tastings_is_empty_list(session: AsyncSession) -> None:
    wine = Wine(name="Fresh", source_url="https://wine.com.br/fresh")
    session.add(wine)
    await session.commit()
    await session.refresh(wine, attribute_names=["tastings"])

    assert wine.tastings == []
