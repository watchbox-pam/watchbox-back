from pydantic import BaseModel
from typing import Optional

class FilmFestival(BaseModel):
    id: str
    name: str
    location: str
    start_date: str  # Format: "DD-MM-YYYY"
    end_date: str
    description: str
    website: Optional[str] = None

    class Config:
        from_attributes = True
        