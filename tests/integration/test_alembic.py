from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

RUN_DB_TESTS = os.environ.get("WINECOLLECTOR_RUN_DB_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_DB_TESTS,
    reason=(
        "set WINECOLLECTOR_RUN_DB_TESTS=1 with a reachable Postgres at "
        "DATABASE_URL to exercise Alembic against the real database"
    ),
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_alembic_current_runs() -> None:
    """``alembic current`` exits 0 against an empty database. No migrations
    exist in task_02; the command should still introspect the configuration
    and connect."""
    result = subprocess.run(
        ["alembic", "current"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"alembic current failed: stdout={result.stdout!r} " f"stderr={result.stderr!r}"
    )


def test_alembic_upgrade_head_runs() -> None:
    """``alembic upgrade head`` is callable. With no migrations in task_02,
    it is a no-op but the command must still exit 0."""
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"alembic upgrade head failed: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )
