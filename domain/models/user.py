from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class User:
    id: str
    username: str
    email: str
    password: str
    salt: str
    country: str
    birthdate: date
    profile_picture_path: str
    banner_path: str
    is_private: bool
    history_private: bool
    adult_content: bool
    last_connection: datetime
    created_at: datetime