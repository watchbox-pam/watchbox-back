from typing import Protocol, List
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion

class IRecommendationService(Protocol):
    def get_by_emotion(self, emotion: Emotion, limit: int = 10) -> List[MovieListItem]:
        ...