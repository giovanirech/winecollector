"""create wine_tastings table

Revision ID: c235c0c3e0e8
Revises: c5320d40b60b
Create Date: 2026-05-22 12:23:43.628886+00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c235c0c3e0e8"
down_revision: str | None = "c5320d40b60b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wine_tastings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("wine_id", sa.Integer(), nullable=False),
        sa.Column(
            "tasted_at",
            sa.Date(),
            server_default=sa.func.current_date(),
            nullable=False,
        ),
        sa.Column("notes_visual", sa.Text(), nullable=True),
        sa.Column("notes_olfactory", sa.Text(), nullable=True),
        sa.Column("notes_palate", sa.Text(), nullable=True),
        sa.Column("memories", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["wine_id"],
            ["wines.id"],
            name="fk_wine_tastings_wine_id_wines",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_wine_tastings_wine_id"),
        "wine_tastings",
        ["wine_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_wine_tastings_wine_id"), table_name="wine_tastings")
    op.drop_table("wine_tastings")
