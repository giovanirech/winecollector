"""create wines table

Revision ID: c5320d40b60b
Revises: b42234b42d44
Create Date: 2026-05-21 22:46:54.066470+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5320d40b60b"
down_revision: str | None = "b42234b42d44"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("winery", sa.String(length=255), nullable=True),
        sa.Column("vintage", sa.Integer(), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("region", sa.String(length=255), nullable=True),
        sa.Column("wine_type", sa.String(length=32), nullable=True),
        sa.Column("sweetness", sa.String(length=32), nullable=True),
        sa.Column("grapes", sa.String(length=255), nullable=True),
        sa.Column("aging", sa.String(length=255), nullable=True),
        sa.Column("alcohol_content", sa.String(length=32), nullable=True),
        sa.Column("serving_temperature", sa.String(length=64), nullable=True),
        sa.Column("aging_potential_years", sa.Integer(), nullable=True),
        sa.Column("visual_notes", sa.Text(), nullable=True),
        sa.Column("olfactory_notes", sa.Text(), nullable=True),
        sa.Column("palate_notes", sa.Text(), nullable=True),
        sa.Column("sommelier_notes", sa.Text(), nullable=True),
        sa.Column("food_pairing", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=1024), nullable=True),
        sa.Column("image_path", sa.String(length=512), nullable=True),
        sa.Column("source_url", sa.String(length=1024), nullable=False),
        sa.Column(
            "scrape_status",
            sa.String(length=16),
            server_default="manual",
            nullable=False,
        ),
        sa.Column(
            "stock",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "purchased_at",
            sa.Date(),
            server_default=sa.func.current_date(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("stock >= 0", name="ck_wines_stock_non_negative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wines_source_url"), "wines", ["source_url"], unique=True)
    op.create_index(op.f("ix_wines_wine_type"), "wines", ["wine_type"], unique=False)
    op.create_index(op.f("ix_wines_winery"), "wines", ["winery"], unique=False)
    op.create_index(
        op.f("ix_wines_purchased_at"), "wines", ["purchased_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_wines_purchased_at"), table_name="wines")
    op.drop_index(op.f("ix_wines_winery"), table_name="wines")
    op.drop_index(op.f("ix_wines_wine_type"), table_name="wines")
    op.drop_index(op.f("ix_wines_source_url"), table_name="wines")
    op.drop_table("wines")
