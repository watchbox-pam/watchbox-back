from datetime import date
from dataclasses import dataclass


@dataclass(frozen=True)
class Movie:
    id: int
    adult: bool
    backdrop_path: str
    budget: int
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