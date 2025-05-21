from dataclasses import dataclass
from datetime import datetime

from pydantic import UUID4


@dataclass(frozen=True)
class UserInfo:
    username: str
    picture: str

@dataclass(frozen=True)
class Review:
    id: str
    rating: int | None
    comment: str | None
    isSpoiler: bool
    movieId: int | None
    tvId: int | None
    tvEpisodeId: int | None
    userId: UUID4
    createdAt: datetime
    user: UserInfo | None
