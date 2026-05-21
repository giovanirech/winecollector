"""SQLAlchemy declarative models.

Importing this package eagerly registers every model on
:attr:`winecollector.database.Base.metadata`, which is what
``migrations/env.py`` consumes for Alembic autogenerate.
"""

from __future__ import annotations

from winecollector.database import Base
from winecollector.models.user import User

__all__ = ["Base", "User"]
