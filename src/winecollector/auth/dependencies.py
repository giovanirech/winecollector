"""``FastAPIUsers`` instance and the ``current_active_user`` dependency.

Every protected route should declare ``Depends(current_active_user)``.

The default ``fastapi-users`` register router is intentionally NOT mounted
here per ADR-005 — the first-run signup flow is custom (task_05).
"""

from __future__ import annotations

import uuid

from fastapi_users import FastAPIUsers

from winecollector.auth.backend import auth_backend
from winecollector.auth.manager import get_user_manager
from winecollector.models import User

fastapi_users: FastAPIUsers[User, uuid.UUID] = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
