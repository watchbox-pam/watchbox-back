"""quiz_question unique constraint

Revision ID: b3c1d2e4f5a6
Revises: f54848dc27fe
Create Date: 2026-04-26 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'b3c1d2e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'f54848dc27fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DELETE FROM quiz_question
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM quiz_question
            GROUP BY genre_slug, movie_id, question_type
        )
    """)
    op.create_unique_constraint(
        'uq_quiz_question_slug_movie_type',
        'quiz_question',
        ['genre_slug', 'movie_id', 'question_type']
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_quiz_question_slug_movie_type',
        'quiz_question',
        type_='unique'
    )
