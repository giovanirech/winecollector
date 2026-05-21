"""``FastAPIUsers`` instance and the ``current_active_user`` dependency.

Every protected route should declare ``Depends(current_active_user)``.

The default ``fastapi-users`` register router is intentionally NOT mounted
here per ADR-005 — the first-run signup flow is custom (task_05).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi_users import FastAPIUsers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from winecollector.auth.backend import auth_backend
from winecollector.auth.manager import get_user_manager
from winecollector.database import get_session
from winecollector.models import User

fastapi_users: FastAPIUsers[User, uuid.UUID] = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)


async def signup_open(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> bool:
    """Return ``True`` while the ``users`` table holds zero rows.

    Powers the self-closing signup gate (ADR-005): the moment the first
    user exists, ``GET/POST /signup`` returns 404 and the registration
    surface effectively disappears.
    """
    result = await session.execute(select(User.id).limit(1))
    return result.first() is None
