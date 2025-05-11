from typing import List

from domain.interfaces.repositories.i_review_repository import IReviewRepository
from domain.interfaces.services.i_review_service import IReviewService
from domain.models.review import Review


class ReviewService(IReviewService):
    def __init__(self, repository: IReviewRepository):
        self.repository = repository

    def create_review(self, review: Review) -> bool:
        review_creation = self.repository.create_review(review)
        return review_creation

    def get_reviews_by_media(self, media_id: int) -> List[Review]:
        return self.repository.get_reviews_by_media(media_id)