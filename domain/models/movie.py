from datetime import date
from dataclasses import dataclass

class Genre:
    id: int
    name: str

@dataclass(frozen=True)
class Movie:
    id: int
    adult: bool
    backdrop_path: str
    budget: int
    genres: list[Genre]
    original_language: str
    original_title: str
    overview: str
    poster_path: str
    release_date: date
    revenue: int
    runtime: int
    status: str
    title: str
    video: str
    infos_complete: bool