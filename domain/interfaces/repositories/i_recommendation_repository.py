from typing import Protocol, List

from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movieReview import MovieReview


class IRecommendationRepository(Protocol):
    def find_by_ids_recommendation(self, ids: List[int]) -> List[MovieRecommendation]:
        ...

    def find_by_genres(self, genres: List[int]) -> List[MovieRecommendation]:
        ...

    def find_with_review(self, user_id: str, movie_ids: List[int]) -> List[MovieReview]:
        ...

    def get_all_reviews(self) -> List[dict]:
        ...

    def get_swipe_movie_ids(self, user_id: str) -> List[int]:
        ...

    def get_all_implicit_feedback(self) -> List[dict]:
        ...

    def get_skip_movie_ids(self, user_id: str) -> List[int]:
        ...