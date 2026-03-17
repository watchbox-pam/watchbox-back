from datetime import date
from dataclasses import dataclass

from domain.models.genre import Genre
from domain.models.credits import Cast, Crew

@dataclass(frozen=True)
class CreatedByListItem:
    id: int
    credit_id: str
    name: str
    gender: int
    profile_path: str

@dataclass(frozen=True)
class LastEpisodeToAir:
    id: int
    name: str
    overview: str
    vote_average: int
    vote_count: int
    air_date: date
    episode_number: int
    production_code: str
    runtime: int
    season_number: int
    show_id: int
    still_path: str

@dataclass(frozen=True)
class NetworksListItem:
    id: int
    logo_path: str
    name: str
    origin_country: str

@dataclass(frozen=True)
class ProductionCompaniesListItem:
    id: int
    logo_path: str
    name: str
    origin_country: str

@dataclass(frozen=True)
class ProductionCountriesListItem:
    iso_3166_1: str
    name: str

@dataclass(frozen=True)
class SeasonsListItem:
    air_date: date
    episode_count: int
    id: int
    name: str
    overview: str
    poster_path: str
    season_number: int
    vote_average: int

@dataclass(frozen=True)
class SpokenLanguagesListItem:
    english_name: str
    iso_639_1: str
    name: str

@dataclass(frozen=True)
class Tv:
    backdrop_path: str
    adult: bool
    created_by: list[CreatedByListItem]
    episode_run_time: list[int]
    first_air_date: date
    genres: list[Genre]
    homepage: str
    id: int
    in_production: bool
    languages: list[str]
    last_air_date: date
    last_episode_to_air: LastEpisodeToAir
    name: str
    next_episode_to_air: str
    networks: list[NetworksListItem]
    number_of_episodes: int
    number_of_seasons: int
    origin_country: list[str]
    original_language: str
    original_name: str
    overview: str
    popularity: int
    poster_path: str
    production_companies: list[ProductionCompaniesListItem]
    production_countries: list[ProductionCountriesListItem]
    seasons: list[SeasonsListItem]
    spoken_languages: list[SpokenLanguagesListItem]
    status: str
    tagline: str
    type: str
    vote_average: int
    vote_count: int