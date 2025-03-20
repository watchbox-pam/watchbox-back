from fastapi import APIRouter, Query
from fastapi.params import Depends
from typing import List

from domain.interfaces.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.i_recommendation_service import IRecommendationService
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion
from repository.recommentation_repository import RecommendationRepository
from service.recommendation_service import RecommendationService

recommendation_router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def get_recommendation_service() -> IRecommendationService:
    repository: IRecommendationRepository = RecommendationRepository()
    return RecommendationService(repository)

@recommendation_router.get("/emotion/{emotion}")
async def get_movies_by_emotion(
    emotion: Emotion,
    limit: int = Query(10, ge=1, le=50),
    service: IRecommendationService = Depends(get_recommendation_service)
) -> List[MovieListItem]:
    """
    Returns a list of movies based on a specific emotion
    :param emotion: the emotion to get movies for
    :param limit: the maximum number of movies to return
    :param service: the service to call to get the movies
    :return: a list of movies matching the emotion
    """
    return service.get_by_emotion(emotion, limit)