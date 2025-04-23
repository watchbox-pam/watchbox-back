from typing import List
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion


class RecommendationService(IRecommendationService):
    def __init__(self, repository: IRecommendationRepository):
        self.repository = repository

    def get_by_emotion(self, emotion: Emotion, limit: int = 10) -> List[MovieListItem]:
        return self.repository.get_by_emotion(emotion, limit)