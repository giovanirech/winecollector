from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from winecollector.config import get_settings


class Base(DeclarativeBase):
    """Shared declarative base — every model in :mod:`winecollector.models`
    inherits from this so Alembic sees a single ``MetaData`` instance."""


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        future=True,
    )


@lru_cache(maxsize=1)
def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a single :class:`AsyncSession` per
    request and closes it on exit."""
    async with _get_sessionmaker()() as session:
        yield session
