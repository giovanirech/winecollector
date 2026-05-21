"""Unit tests for the :class:`UserManager` hooks."""

from __future__ import annotations

import logging
import uuid
from unittest.mock import AsyncMock

import pytest

from winecollector.auth.manager import UserManager


@pytest.fixture
def manager() -> UserManager:
    """Build a :class:`UserManager` with a stub user-database adapter.

    The hooks under test never touch the database, so an :class:`AsyncMock`
    is sufficient. Real CRUD goes through fastapi-users in integration.
    """
    return UserManager(AsyncMock())


async def test_on_after_register_logs_event(
    manager: UserManager, caplog: pytest.LogCaptureFixture
) -> None:
    user = type(
        "FakeUser",
        (),
        {"email": "owner@example.com", "id": uuid.uuid4()},
    )()
    caplog.set_level(logging.INFO, logger="winecollector.auth.manager")

    await manager.on_after_register(user)  # type: ignore[arg-type]

    records = [r for r in caplog.records if r.name == "winecollector.auth.manager"]
    assert records, "expected an INFO log on registration"
    assert records[0].levelno == logging.INFO
    assert "owner@example.com" in records[0].getMessage()


def test_reset_password_token_secret_reuses_settings_secret() -> None:
    from winecollector.config import get_settings

    manager = UserManager(AsyncMock())
    assert manager.reset_password_token_secret == get_settings().SECRET_KEY
    assert manager.verification_token_secret == get_settings().SECRET_KEY
