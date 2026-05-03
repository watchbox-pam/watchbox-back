"""update swipe table structure

Revision ID: 1f1910cd9b62
Revises: 783bf5f19a75
Create Date: 2026-04-18 19:02:29.753254

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f1910cd9b62'
down_revision: Union[str, Sequence[str], None] = '783bf5f19a75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "swipe",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.UUID, nullable=False),
        sa.Column("movie_id", sa.Integer),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["movie_id"], ["movie.id"]),
        sa.UniqueConstraint("user_id", "movie_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
