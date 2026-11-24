"""movie.video varchar -> boolean

Revision ID: d4f8b2c6e1a3
Revises: c7e2a9d41b80
Create Date: 2026-11-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd4f8b2c6e1a3'
down_revision: Union[str, Sequence[str], None] = 'c7e2a9d41b80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Les valeurs existantes sont des chaînes ("True", "false", "1", "", ...).
    # Tout ce qui n'est pas reconnu devient NULL plutôt que de faire échouer la migration.
    op.execute(
        """
        ALTER TABLE movie
        ALTER COLUMN video TYPE BOOLEAN
        USING CASE
            WHEN lower(trim(video)) IN ('true', 't', '1', 'yes', 'y') THEN TRUE
            WHEN lower(trim(video)) IN ('false', 'f', '0', 'no', 'n') THEN FALSE
            ELSE NULL
        END
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE movie
        ALTER COLUMN video TYPE VARCHAR
        USING CASE
            WHEN video IS NULL THEN NULL
            WHEN video THEN 'True'
            ELSE 'False'
        END
        """
    )
