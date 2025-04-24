from datetime import date
from dataclasses import dataclass
from typing import List

from domain.models.genre import Genre
from domain.models.keyword import Keyword
from domain.models.person import PersonDetail


@dataclass()
class MovieRecommendation:
    id: int
    weight: float
    popularity: float
    poster_path: str
    title: str
    genres: List[Genre]
    keywords: List[Keyword]
    cast: List[PersonDetail]
    crew: List[PersonDetail]
