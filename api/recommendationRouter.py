from fastapi import APIRouter
from fastapi.params import Depends

from api.auth.verify_auth_token import check_jwt_token
from api.movieRouter import get_movie_service
from api.playlistRouter import get_playlist_service
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_movie_service import IMovieService
from domain.interfaces.services.i_playlist_service import IPlaylistService
from domain.interfaces.services.i_recommendation_service import IRecommendationService
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

@recommendation_router.get("/recommended/{emotion}")
async def get_recommended_movies(emotion: Emotion, user_id: str = Depends(get_current_user), service: IRecommendationService = Depends(get_recommendation_service)):
    movies = service.get_recommendations(emotion, user_id)
    return movies
