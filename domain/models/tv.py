from datetime import date
from dataclasses import dataclass

from domain.models.genre import Genre

@dataclass(frozen=True)
class TvDetail:
    id: int
    adult: bool
    backdrop_path: str
    genres: list[Genre]
    original_language: str
    original_name: str
    name: str
    overview: str
    poster_path: str
    # release_date: date
    first_air_date: date
    last_air_date: date
    status: str
    video: str
    infos_complete: bool

# class TvVideo