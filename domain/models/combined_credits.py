from dataclasses import dataclass

@dataclass(frozen=True)
class Cast:
    id: int
    adult: bool
    genre_ids: list[int]
    original_language: str
    original_title: str
    overview: str
    popularity: int
    poster_path: str
    release_date: str
    title: str
    video: bool
    vote_average: int
    vote_count: int
    character: str
    credit_id: str
    order: int
    media_type: str
    
@dataclass(frozen=True)
class Crew:
    id: int
    adult: bool
    backdrop_path: str
    genre_ids: list[int]
    original_language: str
    original_title: str
    overview: str
    popularity: int
    poster_path: str
    release_date: str
    title: str
    video: bool
    vote_average: int
    vote_count: int
    credit_id: str
    department: str
    job: str
    media_type: str

@dataclass(frozen=True)
class CombinedCredits:
    cast: list[Cast]
    crew: list[Crew]
    id: int