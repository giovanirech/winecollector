"""``WineTasting`` — degustation log entry.

Shipped in V1 (table + model + relationship) but with no router or
service consumer per ADR-006. Freezing the schema now keeps the JSON
export's ``schema_version`` stable and avoids a Phase-2 schema rush.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from winecollector.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from winecollector.models.wine import Wine


class WineTasting(Base):
    __tablename__ = "wine_tastings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    wine_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tasted_at: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    notes_visual: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes_olfactory: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes_palate: Mapped[str | None] = mapped_column(Text, nullable=True)
    memories: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    wine: Mapped[Wine] = relationship(back_populates="tastings", lazy="selectin")
