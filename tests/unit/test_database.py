from __future__ import annotations

import inspect

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from winecollector.database import (
    Base,
    _get_sessionmaker,
    get_engine,
    get_session,
)


def test_base_is_declarative_base_subclass() -> None:
    assert issubclass(Base, DeclarativeBase)
    assert Base.metadata is not None


def test_get_engine_returns_async_engine() -> None:
    engine = get_engine()
    assert isinstance(engine, AsyncEngine)
    # asyncpg driver is what TechSpec mandates.
    assert "asyncpg" in str(engine.url)


def test_get_engine_returns_cached_singleton() -> None:
    assert get_engine() is get_engine()


def test_sessionmaker_is_async_and_bound_to_engine() -> None:
    sm = _get_sessionmaker()
    assert isinstance(sm, async_sessionmaker)
    # The sessionmaker yields AsyncSession instances.
    assert sm.class_ is AsyncSession  # type: ignore[attr-defined]


def test_get_session_is_async_generator_function() -> None:
    assert inspect.isasyncgenfunction(get_session)


def test_get_session_yields_async_session() -> None:
    """The async generator wraps the sessionmaker; the yielded value is an
    ``AsyncSession``. We verify by inspecting the sessionmaker class binding
    rather than by opening a real connection (no DB required for unit tests)."""
    sm = _get_sessionmaker()
    instance = sm()
    try:
        assert isinstance(instance, AsyncSession)
    finally:
        # Mark the session closed without awaiting (we never opened a
        # connection); explicit cleanup avoids unraisable warnings.
        instance.sync_session.close()
