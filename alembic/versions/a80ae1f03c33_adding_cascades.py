"""adding cascades”

Revision ID: a80ae1f03c33
Revises: 8c6de4d1e9d6
Create Date: 2026-03-18 15:40:28.911224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a80ae1f03c33'
down_revision: Union[str, Sequence[str], None] = '8c6de4d1e9d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('playlist_user_id_fkey', 'playlist', type_='foreignkey')
    op.create_foreign_key(
        'playlist_user_id_fkey',
        'playlist',
        'user',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('playlist_user_id_fkey', 'playlist', type_='foreignkey')
    op.create_foreign_key(
        'playlist_user_id_fkey',
        'playlist',
        'user',
        ['user_id'],
        ['id']
    )
    # ### end Alembic commands ###