"""add user_media_provider table and user.onboarding_completed_at

Revision ID: e5a7c3f90b12
Revises: d8b4e2f61a3c
Create Date: 2026-11-24 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5a7c3f90b12'
down_revision: Union[str, Sequence[str], None] = 'd8b4e2f61a3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_media_provider',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('media_provider_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_media_provider_user_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['media_provider_id'], ['media_provider.id'], name='user_media_provider_media_provider_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'media_provider_id', name='user_media_provider_pkey'),
    )

    op.add_column('user', sa.Column('onboarding_completed_at', sa.DateTime(), nullable=True))
    # Les comptes existants ne doivent pas repasser par l'onboarding
    op.execute('UPDATE "user" SET onboarding_completed_at = now()')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'onboarding_completed_at')
    op.drop_table('user_media_provider')
