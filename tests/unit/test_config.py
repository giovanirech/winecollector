from __future__ import annotations

import pytest
from pydantic import ValidationError

from winecollector.config import Settings, get_settings


def test_settings_loads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_USER", "alice")
    monkeypatch.setenv("POSTGRES_PASSWORD", "topsecret")
    monkeypatch.setenv("POSTGRES_DB", "cellar")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://alice:topsecret@localhost:5432/cellar",
    )
    monkeypatch.setenv("SECRET_KEY", "k" * 64)
    monkeypatch.setenv("ALGORITHM", "HS512")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("IMAGES_DIR", "/tmp/img")
    monkeypatch.setenv("SCRAPER_TIMEOUT", "20.5")
    monkeypatch.setenv("SCRAPER_USER_AGENT", "WC-Test/0.1")
    monkeypatch.setenv("ENVIRONMENT", "production")

    s = Settings(_env_file=None)  # type: ignore[call-arg]

    assert s.POSTGRES_USER == "alice"
    assert s.POSTGRES_PASSWORD == "topsecret"
    assert s.POSTGRES_DB == "cellar"
    assert s.DATABASE_URL.startswith("postgresql+asyncpg://alice:")
    assert len(s.SECRET_KEY) == 64
    assert s.ALGORITHM == "HS512"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert s.IMAGES_DIR == "/tmp/img"
    assert s.SCRAPER_TIMEOUT == 20.5
    assert s.SCRAPER_USER_AGENT == "WC-Test/0.1"
    assert s.ENVIRONMENT == "production"


def test_settings_rejects_short_secret_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SECRET_KEY", "x")
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)  # type: ignore[call-arg]
    assert "SECRET_KEY" in str(exc_info.value)


def test_settings_rejects_invalid_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SECRET_KEY", "x" * 64)
    monkeypatch.setenv("ENVIRONMENT", "staging")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_get_settings_returns_cached_singleton() -> None:
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert first is second
    get_settings.cache_clear()
