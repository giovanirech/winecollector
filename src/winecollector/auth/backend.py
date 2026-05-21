"""Authentication backend assembly: ``CookieTransport`` + ``JWTStrategy``.

Configuration is sourced from :mod:`winecollector.config` so every value
(secret, lifetime, cookie ``secure`` flag) flows from ``Settings``. The
cookie attributes follow ADR-004:

- ``httponly=True`` always — block XSS token theft.
- ``secure=True`` only when ``ENVIRONMENT=='production'`` — local dev
  uses plain HTTP.
- ``samesite='lax'`` — allow top-level navigation, block cross-site POSTs.
- ``max_age`` matches ``ACCESS_TOKEN_EXPIRE_MINUTES``.
"""

from __future__ import annotations

from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

from winecollector.config import Settings, get_settings

COOKIE_NAME = "winecollector_auth"


def build_cookie_transport(settings: Settings) -> CookieTransport:
    """Build a :class:`CookieTransport` whose flags follow ``settings``."""
    return CookieTransport(
        cookie_name=COOKIE_NAME,
        cookie_max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        cookie_secure=settings.ENVIRONMENT == "production",
        cookie_httponly=True,
        cookie_samesite="lax",
    )


def get_jwt_strategy() -> JWTStrategy:
    """Build a :class:`JWTStrategy` from current ``Settings`` on each call.

    Returning a fresh strategy lets tests swap ``SECRET_KEY`` / expiry
    between cases via ``Settings`` overrides without rebuilding the backend.
    """
    settings = get_settings()
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        algorithm=settings.ALGORITHM,
    )


auth_backend: AuthenticationBackend = AuthenticationBackend(
    name="cookie-jwt",
    transport=build_cookie_transport(get_settings()),
    get_strategy=get_jwt_strategy,
)
