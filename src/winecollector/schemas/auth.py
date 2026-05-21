"""User-facing auth schemas consumed by ``fastapi-users``."""

from __future__ import annotations

import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Outgoing user payload — the password is intentionally not exposed."""


class UserCreate(schemas.BaseUserCreate):
    """Incoming payload for the first-run signup form."""
