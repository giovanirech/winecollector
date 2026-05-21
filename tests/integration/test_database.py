from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from winecollector.database import _get_sessionmaker

RUN_DB_TESTS = os.environ.get("WINECOLLECTOR_RUN_DB_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_DB_TESTS,
    reason=(
        "set WINECOLLECTOR_RUN_DB_TESTS=1 with a reachable Postgres at "
        "DATABASE_URL to exercise the real async engine"
    ),
)


async def test_session_executes_select_1() -> None:
    async with _get_sessionmaker()() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
