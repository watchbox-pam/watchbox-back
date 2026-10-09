from fastapi import APIRouter, BackgroundTasks, status
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.interfaces.services.i_review_service import IReviewService
from domain.models.review import Review
from repository.playlist_repository import PlaylistRepository
from repository.review_repository import ReviewRepository
from service.review_service import ReviewService
from service.training_service import TrainingService
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from repository.recommentation_repository import RecommendationRepository

review_router = APIRouter(prefix="/reviews", tags=["Reviews"])

TRAINING_THRESHOLD = 50

def get_review_service() -> IReviewService:
    repository: IReviewRepository = ReviewRepository()
    playlist_repository: IPlaylistRepository = PlaylistRepository()
    return ReviewService(repository, playlist_repository)

def get_review_repository() -> ReviewRepository:
    return ReviewRepository()

@review_router.post("")
async def create_review(
    review: Review,
    background_tasks: BackgroundTasks,
    service: IReviewService = Depends(get_review_service),
    repo: ReviewRepository = Depends(get_review_repository)
):
    try:
        is_new_rating = service.create_review(review)
        if is_new_rating:
            new_count = repo.increment_counter()
            if new_count >= TRAINING_THRESHOLD:
                repo.reset_counter()
                background_tasks.add_task(
                    TrainingService(RecommendationRepository(), PlaylistRepository()).build_and_train
                )
                print(f"Réentraînement déclenché en arrière-plan après {TRAINING_THRESHOLD} nouveaux ratings")
        return True
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@review_router.get("/movie/{movie_id}")
async def get_reviews(movie_id: int, service: IReviewService = Depends(get_review_service)):
    try:
        reviews = service.get_reviews_by_media(movie_id)
        return reviews
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))