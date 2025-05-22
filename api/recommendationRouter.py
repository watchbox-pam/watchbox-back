from fastapi import APIRouter
from fastapi.params import Depends

from api.auth.verify_auth_token import check_jwt_token
from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.emotion import Emotion
from repository.playlist_repository import PlaylistRepository
from repository.recommentation_repository import RecommendationRepository
from service.recommendation_service import RecommendationService

recommendation_router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def get_recommendation_service() -> IRecommendationService:
    repository: IRecommendationRepository = RecommendationRepository()
    playlist_repository: IPlaylistRepository = PlaylistRepository()
    return RecommendationService(repository, playlist_repository)

def get_current_user(user_id: str = Depends(check_jwt_token)):
    return user_id

@recommendation_router.get("/recommended/{emotion}")
async def get_recommended_movies(emotion: Emotion, user_id: str = Depends(get_current_user), service: IRecommendationService = Depends(get_recommendation_service)):
    movies = service.get_recommendations(emotion, user_id)
    return movies
