"""``UserManager`` implementation used by ``fastapi-users``."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from winecollector.auth.user_db import get_user_db
from winecollector.config import get_settings
from winecollector.models import User

logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Issues and resets password tokens; emits domain events post-register.

    Token secrets reuse ``SECRET_KEY`` from ``Settings``: the same key signs
    JWTs and password-reset/verify tokens. ADR-005 leaves no public register
    surface, so ``on_after_register`` only ever fires for the first-run
    signup flow.
    """

    @property
    def reset_password_token_secret(self) -> str:
        return get_settings().SECRET_KEY

    @property
    def verification_token_secret(self) -> str:
        return get_settings().SECRET_KEY

    async def on_after_register(
        self, user: User, request: Request | None = None
    ) -> None:
        logger.info("user_registered email=%s id=%s", user.email, user.id)


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase[User, uuid.UUID], Depends(get_user_db)],
) -> AsyncIterator[UserManager]:
    """FastAPI dependency that yields a :class:`UserManager` per request."""
    yield UserManager(user_db)
