from __future__ import annotations

import os
import shutil
import subprocess
import time

import pytest

RUN_DOCKER_TESTS = os.environ.get("WINECOLLECTOR_RUN_DOCKER_TESTS") == "1"


pytestmark = pytest.mark.skipif(
    not RUN_DOCKER_TESTS,
    reason="set WINECOLLECTOR_RUN_DOCKER_TESTS=1 to run docker-compose boot tests",
)


def _docker_available() -> bool:
    return shutil.which("docker") is not None


def test_db_healthcheck() -> None:
    if not _docker_available():
        pytest.skip("docker CLI not available on PATH")

    subprocess.run(
        ["docker", "compose", "up", "-d", "db"],
        check=True,
        capture_output=True,
    )
    try:
        deadline = time.monotonic() + 60
        last_status = ""
        while time.monotonic() < deadline:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json", "db"],
                check=True,
                capture_output=True,
                text=True,
            )
            last_status = result.stdout
            if '"Health":"healthy"' in last_status or '"healthy"' in last_status:
                return
            time.sleep(2)
        pytest.fail(f"db did not become healthy in time. last status: {last_status!r}")
    finally:
        subprocess.run(
            ["docker", "compose", "down"],
            check=False,
            capture_output=True,
        )
