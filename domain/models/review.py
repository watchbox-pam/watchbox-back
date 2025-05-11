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
    has_spoiler: bool
    movie_id: int | None
    tv_id: int | None
    tv_episode_id: int | None
    user_id: UUID4
    created_at: datetime
    user: UserInfo | None
