from dataclasses import dataclass

from pydantic import UUID4


@dataclass(frozen=True)
class MovieReview:
    rating: int | None
    movie_id: int | None
    user_id: UUID4
