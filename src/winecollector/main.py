from __future__ import annotations

from fastapi import FastAPI

from winecollector.auth.backend import auth_backend
from winecollector.auth.dependencies import fastapi_users
from winecollector.routers.auth import router as auth_router

app = FastAPI(title="WineCollector", version="0.1.0")

# Custom auth surface FIRST so our /auth/logout takes precedence over
# fastapi-users' default 204 logout (which is mounted below).
app.include_router(auth_router)

# fastapi-users' auth router provides POST /auth/login. It also provides
# POST /auth/logout, but our custom logout above wins by route order.
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
)
