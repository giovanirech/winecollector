"""Unit tests for the authentication backend wiring."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

from winecollector.auth.backend import (
    COOKIE_NAME,
    auth_backend,
    build_cookie_transport,
    get_jwt_strategy,
)
from winecollector.config import Settings, get_settings


@pytest.fixture
def _settings_cache_reset() -> Iterator[None]:
    """Force ``get_settings`` to re-read the environment for each test that
    manipulates ``os.environ``."""
    get_settings.cache_clear()
    try:
        yield
    finally:
        get_settings.cache_clear()


def _make_settings(**overrides: object) -> Settings:
    defaults: dict[str, object] = {
        "SECRET_KEY": "k" * 64,
        "ENVIRONMENT": "development",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 60,
    }
    defaults.update(overrides)
    return Settings(**defaults)  # type: ignore[arg-type]


def test_auth_backend_uses_cookie_jwt_name() -> None:
    assert isinstance(auth_backend, AuthenticationBackend)
    assert auth_backend.name == "cookie-jwt"
    assert isinstance(auth_backend.transport, CookieTransport)


def test_jwt_strategy_uses_settings_secret(
    monkeypatch: pytest.MonkeyPatch, _settings_cache_reset: None
) -> None:
    custom_secret = "z" * 64
    monkeypatch.setenv("SECRET_KEY", custom_secret)
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    strategy = get_jwt_strategy()

    assert isinstance(strategy, JWTStrategy)
    secret = strategy.secret
    # ``JWTStrategy.secret`` accepts ``str | SecretStr``; normalize before
    # comparison so the test is agnostic to upstream typing changes.
    secret_value = (
        secret.get_secret_value() if hasattr(secret, "get_secret_value") else secret
    )
    assert secret_value == custom_secret
    assert strategy.lifetime_seconds == 30 * 60


def test_cookie_transport_uses_settings_max_age() -> None:
    settings = _make_settings(ACCESS_TOKEN_EXPIRE_MINUTES=45)

    transport = build_cookie_transport(settings)

    assert transport.cookie_max_age == 45 * 60
    assert transport.cookie_name == COOKIE_NAME


@pytest.mark.parametrize(
    ("environment", "expected_secure"),
    [("development", False), ("production", True)],
)
def test_cookie_secure_flag_follows_environment(
    environment: str, expected_secure: bool
) -> None:
    settings = _make_settings(ENVIRONMENT=environment)

    transport = build_cookie_transport(settings)

    assert transport.cookie_secure is expected_secure


def test_cookie_transport_is_httponly_and_samesite_lax() -> None:
    transport = build_cookie_transport(_make_settings())

    assert transport.cookie_httponly is True
    assert transport.cookie_samesite == "lax"
