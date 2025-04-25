from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class PlaylistMedia:
    playlist_id: str
    movie_id: int
    tv_id: int
    add_date: datetime