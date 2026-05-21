from __future__ import annotations

import tomllib
from pathlib import Path

REQUIRED_RUNTIME_DEPENDENCIES = {
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "asyncpg",
    "alembic",
    "fastapi-users",
    "pydantic",
    "pydantic-settings",
    "httpx",
    "beautifulsoup4",
    "jinja2",
    "python-multipart",
    "pillow",
}

REQUIRED_DEV_DEPENDENCIES = {
    "ruff",
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "factory-boy",
}


def _load_pyproject() -> dict:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with pyproject_path.open("rb") as fh:
        return tomllib.load(fh)


def test_pinned_dependencies_present() -> None:
    pyproject = _load_pyproject()
    runtime = set(pyproject["tool"]["poetry"]["dependencies"].keys()) - {"python"}
    missing = REQUIRED_RUNTIME_DEPENDENCIES - runtime
    assert not missing, f"missing runtime dependencies: {sorted(missing)}"


def test_pinned_dev_dependencies_present() -> None:
    pyproject = _load_pyproject()
    dev_group = pyproject["tool"]["poetry"]["group"]["dev"]["dependencies"]
    missing = REQUIRED_DEV_DEPENDENCIES - set(dev_group.keys())
    assert not missing, f"missing dev dependencies: {sorted(missing)}"


def test_ruff_line_length_is_88() -> None:
    pyproject = _load_pyproject()
    assert pyproject["tool"]["ruff"]["line-length"] == 88


def test_pytest_asyncio_mode_is_auto() -> None:
    pyproject = _load_pyproject()
    assert pyproject["tool"]["pytest"]["ini_options"]["asyncio_mode"] == "auto"
