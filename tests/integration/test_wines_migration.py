"""Integration tests for the ``wines`` table — schema constraints and defaults.

Uses an in-memory aiosqlite engine so the suite runs without Postgres. The
unique index, the ``CHECK (stock >= 0)`` constraint, and the
``server_default`` clauses are all portable to SQLite, which is the
ground truth this test exercises. A separate Postgres-gated test runs in
CI for engine-specific behavior (timestamp ``ON UPDATE``).
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from winecollector.database import Base
from winecollector.models import Wine


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


async def test_insert_minimum_wine_succeeds(session: AsyncSession) -> None:
    wine = Wine(name="Casillero del Diablo", source_url="https://wine.com.br/prod1")
    session.add(wine)
    await session.commit()

    fetched = (
        await session.execute(
            select(Wine).where(Wine.source_url == "https://wine.com.br/prod1")
        )
    ).scalar_one()

    assert fetched.id is not None
    assert fetched.name == "Casillero del Diablo"
    # server defaults populated
    assert fetched.stock == 1
    assert fetched.scrape_status == "manual"
    assert fetched.purchased_at is not None
    assert fetched.created_at is not None
    assert fetched.updated_at is not None


async def test_duplicate_source_url_raises_integrity_error(
    session: AsyncSession,
) -> None:
    session.add(Wine(name="Wine A", source_url="https://wine.com.br/prod-dup"))
    await session.commit()

    session.add(Wine(name="Wine B", source_url="https://wine.com.br/prod-dup"))
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_stock_negative_check_blocks_negative_value(
    session: AsyncSession,
) -> None:
    session.add(
        Wine(
            name="Negative Stock",
            source_url="https://wine.com.br/prod-neg",
            stock=-1,
        )
    )
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_null_name_or_source_url_raises_integrity_error(
    session: AsyncSession,
) -> None:
    session.add(Wine(name=None, source_url="https://wine.com.br/prod-null-name"))  # type: ignore[arg-type]
    with pytest.raises(IntegrityError):
        await session.commit()
