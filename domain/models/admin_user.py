from datetime import date
from typing import Optional

from pydantic import BaseModel


class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    birthdate: Optional[date] = None
    profile_picture_path: Optional[str] = None
    banner_path: Optional[str] = None

    is_private: Optional[bool] = None
    history_private: Optional[bool] = None
    adult_content: Optional[bool] = None
    is_verified: Optional[bool] = None

class AdminUserCreate(BaseModel):
    username: str
    email: str
    password: str
    salt: str

    country: Optional[str] = None
    birthdate: date

    profile_picture_path: Optional[str] = None
    banner_path: Optional[str] = None

    is_private: bool = False
    history_private: bool = False
    adult_content: bool = False
    is_verified: bool = True
