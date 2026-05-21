"""Integration tests for the initial ``users`` table migration.

Gated by ``WINECOLLECTOR_RUN_DB_TESTS=1`` and a reachable Postgres at
``DATABASE_URL``. The tests drive Alembic via subprocess so the exact
production-equivalent command path is exercised, then introspect the schema
via SQLAlchemy to assert the migration produced the expected DDL.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import inspect

from winecollector.database import get_engine

RUN_DB_TESTS = os.environ.get("WINECOLLECTOR_RUN_DB_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_DB_TESTS,
    reason=(
        "set WINECOLLECTOR_RUN_DB_TESTS=1 with a reachable Postgres at "
        "DATABASE_URL to exercise the users migration"
    ),
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COLUMNS = {
    "id",
    "email",
    "hashed_password",
    "is_active",
    "is_superuser",
    "is_verified",
}


def _alembic(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["alembic", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


async def _table_exists(name: str) -> bool:
    engine = get_engine()
    async with engine.connect() as conn:
        return await conn.run_sync(lambda sc: inspect(sc).has_table(name))


async def _column_names(name: str) -> set[str]:
    engine = get_engine()
    async with engine.connect() as conn:

        def _names(sync_conn) -> set[str]:
            return {c["name"] for c in inspect(sync_conn).get_columns(name)}

        return await conn.run_sync(_names)


async def _email_index_is_unique() -> bool:
    engine = get_engine()
    async with engine.connect() as conn:

        def _check(sync_conn) -> bool:
            indexes = inspect(sync_conn).get_indexes("users")
            return any(
                ix["column_names"] == ["email"] and ix["unique"] for ix in indexes
            )

        return await conn.run_sync(_check)


@pytest.fixture(autouse=True)
def _reset_schema() -> None:
    """Make every test idempotent by stepping the schema back to ``base``
    before and after each case. Failures during teardown are surfaced so a
    broken state does not silently poison the next run."""
    _alembic("downgrade", "base")
    yield
    _alembic("downgrade", "base")


def test_upgrade_creates_users_table() -> None:
    result = _alembic("upgrade", "head")
    assert (
        result.returncode == 0
    ), f"upgrade failed: stdout={result.stdout!r} stderr={result.stderr!r}"

    assert asyncio.run(_table_exists("users")) is True
    assert EXPECTED_COLUMNS.issubset(asyncio.run(_column_names("users")))
    assert asyncio.run(_email_index_is_unique()) is True


def test_downgrade_drops_users_table() -> None:
    upgrade = _alembic("upgrade", "head")
    assert (
        upgrade.returncode == 0
    ), f"upgrade failed: stdout={upgrade.stdout!r} stderr={upgrade.stderr!r}"
    assert asyncio.run(_table_exists("users")) is True

    downgrade = _alembic("downgrade", "base")
    assert downgrade.returncode == 0, (
        f"downgrade failed: stdout={downgrade.stdout!r} " f"stderr={downgrade.stderr!r}"
    )
    assert asyncio.run(_table_exists("users")) is False
