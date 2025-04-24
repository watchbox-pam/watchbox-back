from fastapi import APIRouter, Query
from fastapi.params import Depends
from typing import List

from api.auth.verify_auth_token import check_jwt_token
from api.movieRouter import get_movie_service
from api.playlistRouter import get_playlist_service
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_movie_service import IMovieService
from domain.interfaces.services.i_playlist_service import IPlaylistService
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion
from repository.recommentation_repository import RecommendationRepository
from service.recommendation_service import RecommendationService

recommendation_router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def get_recommendation_service() -> IRecommendationService:
    repository: IRecommendationRepository = RecommendationRepository()
    playlist_service: IPlaylistService = get_playlist_service()
    movie_service: IMovieService = get_movie_service()
    return RecommendationService(repository, playlist_service, movie_service)

def get_current_user(user_id: str = Depends(check_jwt_token)):
    return user_id

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


@recommendation_router.get("/recommended/{emotion}")
async def get_recommended_movies(emotion: Emotion, user_id: str = Depends(get_current_user), service: IRecommendationService = Depends(get_recommendation_service)):
    movies = service.get_recommendations(emotion, user_id)
    return movies
