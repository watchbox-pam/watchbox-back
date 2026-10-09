"""remove is_admin from user

Revision ID: c7e2a9d41b80
Revises: ca5ab15df850
Create Date: 2026-10-09 17:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e2a9d41b80'
down_revision: Union[str, Sequence[str], None] = 'ca5ab15df850'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('ALTER TABLE "user" DROP COLUMN IF EXISTS is_admin')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'user',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
