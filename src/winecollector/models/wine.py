"""``Wine`` — the core catalog entity.

Stores every field listed in the TechSpec "Data Models" section. All column
identifiers and stored values for categorical fields (``wine_type``,
``sweetness``, ``scrape_status``) are English; Portuguese is reserved for
UI labels and the CSV export header (see TechSpec "Display layer").

Duplicate detection (ADR-002) is enforced by a unique constraint on the
normalized ``source_url``. ``stock`` is a mutable integer with a
``CHECK (stock >= 0)`` guard.
"""

from __future__ import annotations

import datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from winecollector.database import Base


class Wine(Base):
    __tablename__ = "wines"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_wines_stock_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    winery: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    vintage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wine_type: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    sweetness: Mapped[str | None] = mapped_column(String(32), nullable=True)
    grapes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    aging: Mapped[str | None] = mapped_column(String(255), nullable=True)
    alcohol_content: Mapped[str | None] = mapped_column(String(32), nullable=True)
    serving_temperature: Mapped[str | None] = mapped_column(String(64), nullable=True)
    aging_potential_years: Mapped[int | None] = mapped_column(Integer, nullable=True)

    visual_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    olfactory_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    palate_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sommelier_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    food_pairing: Mapped[str | None] = mapped_column(Text, nullable=True)

    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    source_url: Mapped[str] = mapped_column(
        String(1024), nullable=False, unique=True, index=True
    )
    scrape_status: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default="manual"
    )

    stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    purchased_at: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, server_default=func.current_date(), index=True
    )

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
