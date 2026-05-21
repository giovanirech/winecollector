"""Integration tests for the auth backend.

A throw-away ``/protected`` endpoint is mounted on the real FastAPI app so
the cookie + JWT pipeline is exercised end-to-end. The user-manager and
user-database dependencies are overridden with in-memory fakes so the test
does not require a live Postgres.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from fastapi import Depends
from httpx import ASGITransport, AsyncClient

from winecollector.auth.backend import COOKIE_NAME, auth_backend, get_jwt_strategy
from winecollector.auth.dependencies import current_active_user, fastapi_users
from winecollector.auth.manager import get_user_manager
from winecollector.main import app
from winecollector.models import User

PROTECTED_PATH = "/_test/protected"


class _FakeUserManager:
    """Minimal user-manager stand-in supporting ``.get(id)``.

    fastapi-users' authenticator only calls ``parse_id`` (provided by the
    UUIDIDMixin) and ``get`` during request authentication; everything else
    is exercised in unit tests.
    """

    def __init__(self, user: User) -> None:
        self._user = user

    def parse_id(self, value: Any) -> uuid.UUID:
        return uuid.UUID(str(value))

    async def get(self, user_id: uuid.UUID) -> User:
        if user_id != self._user.id:
            raise LookupError(user_id)
        return self._user


def _build_active_user() -> User:
    user = User()
    user.id = uuid.uuid4()
    user.email = "owner@example.com"
    user.hashed_password = "argon2:placeholder"
    user.is_active = True
    user.is_superuser = False
    user.is_verified = False
    return user


@pytest.fixture
def active_user() -> User:
    return _build_active_user()


@pytest.fixture
def _mounted_protected_route(active_user: User):
    """Mount a protected GET route for the duration of one test, then strip
    it back off so the global app stays clean."""

    async def _read_me(
        user: User = Depends(current_active_user),  # noqa: B008 — FastAPI DI requires call in default
    ) -> dict[str, str]:
        return {"id": str(user.id), "email": user.email}

    app.add_api_route(PROTECTED_PATH, _read_me, methods=["GET"])

    fake_manager = _FakeUserManager(active_user)

    async def _override_user_manager() -> AsyncIterator[_FakeUserManager]:
        yield fake_manager

    app.dependency_overrides[get_user_manager] = _override_user_manager
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_user_manager, None)
        app.router.routes = [
            r for r in app.router.routes if getattr(r, "path", None) != PROTECTED_PATH
        ]


@asynccontextmanager
async def _client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


async def test_unauthenticated_request_to_protected_route_returns_401_or_redirect(
    _mounted_protected_route: None,
) -> None:
    async with _client() as ac:
        response = await ac.get(PROTECTED_PATH)

    # fastapi-users' Authenticator raises 401 by default when no credentials
    # are supplied; some auth flows redirect to /login. Accept either.
    assert response.status_code in {401, 302, 303, 307}


async def test_valid_cookie_grants_access(
    _mounted_protected_route: None, active_user: User
) -> None:
    strategy = get_jwt_strategy()
    token = await strategy.write_token(active_user)

    async with _client() as ac:
        response = await ac.get(PROTECTED_PATH, cookies={COOKIE_NAME: token})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["email"] == active_user.email
    assert body["id"] == str(active_user.id)


def test_fastapi_users_register_router_is_not_mounted() -> None:
    """ADR-005: the default ``/auth/register`` surface is intentionally
    absent — task_04 wires the backend but never mounts the register router."""
    paths = {getattr(r, "path", None) for r in app.router.routes}
    assert "/auth/register" not in paths
    assert fastapi_users is not None
    assert auth_backend is not None
