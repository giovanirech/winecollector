"""Unit tests for the ``signup_open`` dependency."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from winecollector.auth.dependencies import signup_open


def _session_returning(first_row: object | None) -> AsyncMock:
    """Build an :class:`AsyncMock` session whose ``execute(...).first()``
    yields ``first_row``."""
    result = MagicMock()
    result.first.return_value = first_row
    session = AsyncMock()
    session.execute.return_value = result
    return session


@pytest.mark.asyncio
async def test_signup_open_true_when_users_empty() -> None:
    session = _session_returning(None)

    is_open = await signup_open(session)

    assert is_open is True
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_signup_open_false_after_first_user() -> None:
    session = _session_returning(("some-uuid",))

    is_open = await signup_open(session)

    assert is_open is False
    session.execute.assert_awaited_once()
