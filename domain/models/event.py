from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class MovieData(BaseModel):
    id: int
    title: str
    poster_path: str
    vote_average: float

class Event(BaseModel):
    id: str
    date: str  # Format: "DD-MM-YYYY"
    time: str
    title: str
    description: str
    type: Optional[Literal["movie", "show", "custom"]] = "custom"
    movie_data: Optional[MovieData] = None

    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    date: str
    time: str
    title: str
    description: str
    type: Optional[Literal["movie", "show", "custom"]] = "custom"
    movie_data: Optional[MovieData] = None