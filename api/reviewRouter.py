from fastapi import APIRouter, status
from fastapi.params import Depends
from starlette.exceptions import HTTPException
from typing import cast
import uuid

from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.interfaces.services.i_review_service import IReviewService
from domain.interfaces.services.i_user_service import IUserService
from domain.models.review import Review
from domain.models.userLogin import UserLogin
from domain.models.userSignup import UserSignup
from repository.review_repository import ReviewRepository
from service.review_service import ReviewService

review_router = APIRouter(prefix="/review", tags=["Reviews"])


def get_review_service() -> IReviewService:
    repository: IReviewRepository = ReviewRepository()
    return ReviewService(repository)


@review_router.post("/")
async def create_review(review: Review, service: IReviewService = Depends(get_review_service)):
    try:
        review_creation = service.create_review(review)
        if review_creation:
            return True
        else:
            raise HTTPException(status_code=400, detail="La review n'a pas été ajoutée")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))
