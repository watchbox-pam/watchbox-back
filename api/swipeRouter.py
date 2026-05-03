from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from api.auth.verify_auth_token import check_jwt_token
from domain.interfaces.services.i_swipe_service import ISwipeService
from domain.models.swipe import SwipeRequest
from repository.swipe_repository import SwipeRepository
from repository.review_repository import ReviewRepository
from repository.recommentation_repository import RecommendationRepository
from repository.playlist_repository import PlaylistRepository
from service.swipe_service import SwipeService
from service.training_service import TrainingService

swipe_router = APIRouter(prefix="/swipes", tags=["Swipes"])

VALID_DIRECTIONS = {"like", "dislike", "skip"}
TRAINING_THRESHOLD = 50


def get_swipe_service() -> ISwipeService:
    return SwipeService(SwipeRepository())

def get_review_repository() -> ReviewRepository:
    return ReviewRepository()


@swipe_router.post("")
async def create_swipe(
    swipe: SwipeRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(check_jwt_token),
    service: ISwipeService = Depends(get_swipe_service),
    review_repo: ReviewRepository = Depends(get_review_repository)
):
    if swipe.direction not in VALID_DIRECTIONS:
        raise HTTPException(status_code=422, detail="direction must be 'like', 'dislike' or 'skip'")

    try:
        result = service.create_swipe(
            user_id=user_id,
            movie_id=swipe.movie_id,
            direction=swipe.direction
        )

        if not result.get("is_duplicate") and swipe.direction in ("like", "dislike"):
            new_count = review_repo.increment_counter()
            if new_count >= TRAINING_THRESHOLD:
                review_repo.reset_counter()
                background_tasks.add_task(
                    TrainingService(RecommendationRepository(), PlaylistRepository()).build_and_train
                )
                print(f"Réentraînement déclenché en arrière-plan après {TRAINING_THRESHOLD} swipes/reviews")

        return result
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
