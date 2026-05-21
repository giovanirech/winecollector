"""SQLAlchemy user-database dependency for ``fastapi-users``."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from winecollector.database import get_session
from winecollector.models import User


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncIterator[SQLAlchemyUserDatabase[User, uuid.UUID]]:
    """Yield a :class:`SQLAlchemyUserDatabase` bound to the request session."""
    yield SQLAlchemyUserDatabase(session, User)
