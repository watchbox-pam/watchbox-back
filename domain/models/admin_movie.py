from datetime import date
from typing import Optional

from pydantic import BaseModel


class AdminMovieUpdate(BaseModel):
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    budget: Optional[int] = None
    homepage: Optional[str] = None
    imdb_id: Optional[str] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[date] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    title: Optional[str] = None
    video: Optional[str] = None
    infos_complete: Optional[bool] = None


class AdminMovieCreate(BaseModel):
    id: int
    adult: Optional[bool] = None
    backdrop_path: Optional[str] = None
    budget: Optional[int] = None
    homepage: Optional[str] = None
    imdb_id: Optional[str] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    release_date: Optional[date] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    title: Optional[str] = None
    popularity: Optional[float] = None
    video: Optional[str] = None
    infos_complete: Optional[bool] = False
