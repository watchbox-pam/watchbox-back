from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class Playlist:
    id: int
    user_id: int
    title: str
    created_at: datetime = datetime
    is_private: bool = field(default=True)