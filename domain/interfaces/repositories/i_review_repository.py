from typing import Protocol

from domain.models.review import Review


class IReviewRepository(Protocol):
    def create_review(self, review: Review) -> bool:
        ...