from typing import Protocol, List

from domain.models.review import Review


class IReviewService(Protocol):
    def create_review(self, review: Review) -> bool:
        ...

    def get_reviews_by_media(self, media_id: int) -> List[Review]:
        ...