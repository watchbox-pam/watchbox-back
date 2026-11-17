"""review unique user movie

Une seule review par (utilisateur, film). Les doublons existants (requêtes simultanées,
re-notations d'avant le 19/06) sont fusionnés : on garde la note la plus récente, et le
commentaire le plus récent du groupe si la review gardée n'en a pas.

Revision ID: dc145e6e1bf1
Revises: c7e2a9d41b80
Create Date: 2026-11-17 21:05:59.349875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'dc145e6e1bf1'
down_revision: Union[str, Sequence[str], None] = 'c7e2a9d41b80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RANKED = """
    SELECT id, user_id, movie_id,
           ROW_NUMBER() OVER (PARTITION BY user_id, movie_id ORDER BY created_at DESC NULLS LAST, id DESC) AS rank
    FROM review
    WHERE movie_id IS NOT NULL
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f"""
        WITH ranked AS ({RANKED}),
        last_comment AS (
            SELECT DISTINCT ON (user_id, movie_id) user_id, movie_id, comment, has_spoiler_warning
            FROM review
            WHERE movie_id IS NOT NULL AND comment IS NOT NULL
            ORDER BY user_id, movie_id, created_at DESC NULLS LAST, id DESC
        )
        UPDATE review r
        SET comment = lc.comment, has_spoiler_warning = lc.has_spoiler_warning
        FROM ranked k
        JOIN last_comment lc ON lc.user_id = k.user_id AND lc.movie_id = k.movie_id
        WHERE r.id = k.id AND k.rank = 1 AND r.comment IS NULL
    """)
    op.execute(f"DELETE FROM review r USING ({RANKED}) k WHERE r.id = k.id AND k.rank > 1")
    op.create_index(
        'uq_review_user_movie', 'review', ['user_id', 'movie_id'],
        unique=True, postgresql_where=sa.text('movie_id IS NOT NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_review_user_movie', table_name='review', postgresql_where=sa.text('movie_id IS NOT NULL'))
