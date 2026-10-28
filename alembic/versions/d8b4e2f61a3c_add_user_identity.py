"""add user_identity table (Google / Apple), password and salt nullable

Revision ID: d8b4e2f61a3c
Revises: c7e2a9d41b80
Create Date: 2026-10-28 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8b4e2f61a3c'
down_revision: Union[str, Sequence[str], None] = 'c7e2a9d41b80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Comptes externes (Google, Apple) rattachés à un utilisateur Watchbox
    op.create_table(
        'user_identity',
        sa.Column('id', sa.Integer(), sa.Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('provider', sa.String(length=20), nullable=False, comment="'google' ou 'apple'"),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False, comment='Identifiant unique et définitif du compte chez le fournisseur (claim sub)'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_identity_user_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='user_identity_pkey'),
        sa.UniqueConstraint('provider', 'provider_user_id', name='user_identity_provider_subject_key'),
        sa.UniqueConstraint('user_id', 'provider', name='user_identity_user_provider_key'),
    )

    # Un compte créé via Google / Apple n'a ni mot de passe ni sel
    op.alter_column('user', 'password', existing_type=sa.String(length=256), nullable=True)
    op.alter_column('user', 'salt', existing_type=sa.String(length=32), nullable=True)

    # Garde-fou : mot de passe et sel sont tous les deux remplis, ou tous les deux vides
    op.create_check_constraint(
        'user_password_salt_consistency',
        'user',
        '(password IS NULL) = (salt IS NULL)'
    )


def downgrade() -> None:
    """Downgrade schema.

    Attention : échoue s'il existe des comptes sans mot de passe (comptes créés via Google / Apple).
    Il faut les supprimer ou leur définir un mot de passe avant.
    """
    op.drop_constraint('user_password_salt_consistency', 'user', type_='check')
    op.alter_column('user', 'salt', existing_type=sa.String(length=32), nullable=False)
    op.alter_column('user', 'password', existing_type=sa.String(length=256), nullable=False)
    op.drop_table('user_identity')
