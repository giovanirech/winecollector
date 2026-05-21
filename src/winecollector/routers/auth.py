"""Public auth surface: login page, self-closing signup gate, logout.

The actual ``POST /auth/login`` endpoint is mounted from ``fastapi-users``
in :mod:`winecollector.main` so it can set the cookie configured in
task_04. This router owns the *human-facing* HTML routes plus the custom
``POST /auth/logout`` that clears the cookie and redirects to ``/login``
(ADR-004 — server-rendered HTMX flow, no JavaScript on logout).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi_users.exceptions import UserAlreadyExists
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from winecollector.auth.backend import COOKIE_NAME, build_cookie_transport
from winecollector.auth.dependencies import signup_open
from winecollector.auth.manager import UserManager, get_user_manager
from winecollector.config import get_settings
from winecollector.database import get_session
from winecollector.schemas.auth import UserCreate
from winecollector.templates_engine import templates as _default_templates

router = APIRouter()


def _templates() -> Jinja2Templates:
    """Indirection so tests can swap the templates instance if needed."""
    return _default_templates


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> Response:
    return _templates().TemplateResponse(request, "auth/login.html", {})


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(
    request: Request, is_open: Annotated[bool, Depends(signup_open)]
) -> Response:
    if not is_open:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return _templates().TemplateResponse(request, "auth/signup.html", {})


@router.post("/signup")
async def signup_submit(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    is_open: Annotated[bool, Depends(signup_open)],
) -> Response:
    if not is_open:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        payload = UserCreate(email=email, password=password)
    except ValidationError:
        return _templates().TemplateResponse(
            request,
            "auth/signup.html",
            {"error": "E-mail inválido."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        await user_manager.create(payload, safe=True, request=request)
    except UserAlreadyExists:
        # The gate closed between the GET and the POST (e.g. another
        # tab). Drop straight to login.
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(
        "/login?signup=ok", status_code=status.HTTP_303_SEE_OTHER
    )
    return response


@router.post("/auth/logout")
async def logout(request: Request) -> Response:
    """Clear the auth cookie and redirect to ``/login``.

    fastapi-users' default logout returns 204 No Content, which forces a
    JavaScript redirect on the client. We instead expire the cookie and
    issue a 303 so a plain HTML form ``<form action="/auth/logout">``
    works without any JS.
    """
    settings = get_settings()
    transport = build_cookie_transport(settings)
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    # Expire the cookie by setting it to an empty value with max_age=0
    # using the same attributes the login flow used to set it.
    response.set_cookie(
        key=COOKIE_NAME,
        value="",
        max_age=0,
        path=transport.cookie_path,
        domain=transport.cookie_domain,
        secure=transport.cookie_secure,
        httponly=transport.cookie_httponly,
        samesite=transport.cookie_samesite,
    )
    return response
