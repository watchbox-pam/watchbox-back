from typing import Protocol, List

from domain.models.movieRecommendation import MovieRecommendation


class IRecommendationRepository(Protocol):
    def find_by_ids_recommendation(self, ids: List[int]) -> List[MovieRecommendation]:
        ...

    def find_by_genres(self, genres: List[int]) -> List[MovieRecommendation]:
        ...