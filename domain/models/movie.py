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

class PopularMovieListItem:
    id: int
    adult: bool
    backdrop_path: str
    title: str
    origin_language: str
    original_title: str
    overview: str
    poster_path: str
    media_type: str
    genre_ids: list[int]
    popularity: int
    release_date: str
    video: bool
    vote_average: int
    vote_count: int

@dataclass(frozen=True)
class PopularMovieList:
    page: int
    results: list[PopularMovieListItem]
    total_pages: int
    total_results: int