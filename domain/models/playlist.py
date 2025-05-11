from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class Playlist:
    id: str
    user_id: str
    title: str
    is_private: bool = field(default=True)
    created_at: datetime = datetime
