from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

@dataclass(frozen=True)
class Playlist:
    id: str
    user_id: str
    title: str
    is_private: bool = field(default=True)
    created_at: datetime = datetime

class PlaylistUpdateRequest(BaseModel):
    user_id: str
    title: Optional[str] = None
    is_private: Optional[bool] = None
