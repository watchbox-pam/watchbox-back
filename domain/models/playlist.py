from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class Playlist:
    id: str
    user_id: str
    title: str
    created_at: datetime = datetime
    is_private: bool = field(default=True)