"""User model owned by ``fastapi-users``.

Inherits the standard UUID-keyed columns (`id`, `email`, `hashed_password`,
`is_active`, `is_superuser`, `is_verified`) from
:class:`fastapi_users.db.SQLAlchemyBaseUserTableUUID` and binds them to the
project-wide :class:`winecollector.database.Base` so Alembic sees a single
``MetaData`` instance.

The base class defaults ``__tablename__`` to ``"user"``; we override to
``"users"`` to match the TechSpec data-model contract.
"""

from __future__ import annotations

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from winecollector.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
