"""End-to-end integration tests for the signup → login → logout flow.

A throw-away SQLite-in-memory engine is wired via dependency overrides so
the suite does not need a Postgres container. Production stays Postgres
(asyncpg) — the User model's ``GUID`` type degrades to ``CHAR(36)`` on
SQLite, which is exactly the portable fallback ``fastapi-users-db-sqlalchemy``
ships for non-Postgres backends.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import pytest_asyncio
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from winecollector.auth.backend import COOKIE_NAME
from winecollector.auth.user_db import get_user_db
from winecollector.database import Base, get_session
from winecollector.main import app
from winecollector.models import User


@pytest_asyncio.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Per-test SQLite engine + fresh schema."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    """ASGI client with ``get_session`` + ``get_user_db`` overridden to
    point at the in-memory engine."""

    async def _override_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    async def _override_user_db() -> (
        AsyncIterator[SQLAlchemyUserDatabase[User, uuid.UUID]]
    ):
        async with session_factory() as session:
            yield SQLAlchemyUserDatabase(session, User)

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_user_db] = _override_user_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_user_db, None)


async def test_signup_open_returns_form_when_users_empty(
    client: AsyncClient,
) -> None:
    response = await client.get("/signup")
    assert response.status_code == 200
    assert "Criar a primeira conta" in response.text


async def test_signup_creates_first_user(client: AsyncClient) -> None:
    response = await client.post(
        "/signup",
        data={"email": "owner@example.com", "password": "correct-horse-battery"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


async def test_signup_returns_404_after_first_user(client: AsyncClient) -> None:
    # First registration closes the gate.
    first = await client.post(
        "/signup",
        data={"email": "owner@example.com", "password": "correct-horse-battery"},
        follow_redirects=False,
    )
    assert first.status_code == 303

    second = await client.get("/signup")
    assert second.status_code == 404

    repost = await client.post(
        "/signup",
        data={"email": "other@example.com", "password": "another-strong-one"},
        follow_redirects=False,
    )
    # POST also closes — either 404 or the silent fallback redirect to /login.
    assert repost.status_code in {303, 404}


async def test_login_sets_jwt_cookie(client: AsyncClient) -> None:
    # Arrange — create the first user.
    signup = await client.post(
        "/signup",
        data={"email": "owner@example.com", "password": "correct-horse-battery"},
        follow_redirects=False,
    )
    assert signup.status_code == 303

    # Act — POST to fastapi-users' login (OAuth2 form: username/password).
    response = await client.post(
        "/auth/login",
        data={"username": "owner@example.com", "password": "correct-horse-battery"},
    )

    # Assert — fastapi-users cookie backend returns 204 on success.
    assert response.status_code == 204, response.text
    assert COOKIE_NAME in response.cookies
    assert response.cookies[COOKIE_NAME] != ""


async def test_login_with_wrong_password_does_not_set_cookie(
    client: AsyncClient,
) -> None:
    await client.post(
        "/signup",
        data={"email": "owner@example.com", "password": "correct-horse-battery"},
        follow_redirects=False,
    )

    response = await client.post(
        "/auth/login",
        data={"username": "owner@example.com", "password": "wrong-password"},
    )

    assert response.status_code in {400, 401}
    assert COOKIE_NAME not in response.cookies


async def test_logout_clears_jwt_cookie(client: AsyncClient) -> None:
    # Arrange — sign up + log in to obtain the cookie.
    await client.post(
        "/signup",
        data={"email": "owner@example.com", "password": "correct-horse-battery"},
        follow_redirects=False,
    )
    login = await client.post(
        "/auth/login",
        data={"username": "owner@example.com", "password": "correct-horse-battery"},
    )
    assert login.status_code == 204
    assert client.cookies.get(COOKIE_NAME)

    # Act — POST /auth/logout
    logout = await client.post("/auth/logout", follow_redirects=False)

    # Assert — redirect to /login, cookie cleared (empty value + max-age 0).
    assert logout.status_code == 303
    assert logout.headers["location"] == "/login"
    set_cookie = logout.headers.get("set-cookie", "")
    assert COOKIE_NAME in set_cookie
    assert ("Max-Age=0" in set_cookie) or ('=""' in set_cookie) or ("=;" in set_cookie)


async def test_signup_with_invalid_email_returns_400_with_message(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/signup",
        data={"email": "not-an-email", "password": "correct-horse-battery"},
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert "E-mail inválido" in response.text


async def test_login_page_renders_login_form(client: AsyncClient) -> None:
    response = await client.get("/login")
    assert response.status_code == 200
    assert "Entrar" in response.text
    assert 'action="/auth/login"' in response.text
