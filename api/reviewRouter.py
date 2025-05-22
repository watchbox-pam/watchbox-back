from fastapi import APIRouter, status
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.interfaces.services.i_review_service import IReviewService
from domain.models.review import Review
from repository.playlist_repository import PlaylistRepository
from repository.review_repository import ReviewRepository
from service.review_service import ReviewService

review_router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_review_service() -> IReviewService:
    repository: IReviewRepository = ReviewRepository()
    playlist_repository: IPlaylistRepository = PlaylistRepository()
    return ReviewService(repository, playlist_repository)


@review_router.post("")
async def create_review(review: Review, service: IReviewService = Depends(get_review_service)):
    try:
        review_creation = service.create_review(review)
        if review_creation:
            return True
        else:
            raise HTTPException(status_code=400, detail="La review n'a pas été ajoutée")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@review_router.get("/movie/{movie_id}")
async def get_reviews(movie_id: int, service: IReviewService = Depends(get_review_service)):
    try:
        reviews = service.get_reviews_by_media(movie_id)
        return reviews
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
