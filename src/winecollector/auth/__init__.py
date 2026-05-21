"""Authentication backend.

Wires ``fastapi-users`` with a cookie-borne JWT (ADR-004) so HTMX requests
carry credentials without custom JavaScript. The default register router is
intentionally NOT mounted (ADR-005 — first-run signup is handled by a custom
route in task_05).
"""

from __future__ import annotations

from winecollector.auth.backend import (
    auth_backend,
    build_cookie_transport,
    get_jwt_strategy,
)
from winecollector.auth.dependencies import current_active_user, fastapi_users
from winecollector.auth.manager import UserManager, get_user_manager
from winecollector.auth.user_db import get_user_db

__all__ = [
    "UserManager",
    "auth_backend",
    "build_cookie_transport",
    "current_active_user",
    "fastapi_users",
    "get_jwt_strategy",
    "get_user_db",
    "get_user_manager",
]
