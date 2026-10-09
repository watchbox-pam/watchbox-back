import uuid
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class Follower:
    sender_id: str
    receiver_id: str
    followed_at: datetime
