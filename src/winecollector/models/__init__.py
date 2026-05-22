"""SQLAlchemy declarative models.

Importing this package eagerly registers every model on
:attr:`winecollector.database.Base.metadata`, which is what
``migrations/env.py`` consumes for Alembic autogenerate.
"""

from __future__ import annotations

from winecollector.database import Base
from winecollector.models.tasting import WineTasting
from winecollector.models.user import User
from winecollector.models.wine import Wine

__all__ = ["Base", "User", "Wine", "WineTasting"]
