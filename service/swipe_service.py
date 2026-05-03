from domain.interfaces.repositories.i_swipe_repository import ISwipeRepository
from domain.interfaces.services.i_swipe_service import ISwipeService


class SwipeService(ISwipeService):
    def __init__(self, repository: ISwipeRepository):
        self.repository = repository

    def create_swipe(self, user_id: str, movie_id: int, direction: str) -> dict:
        return self.repository.create_swipe(user_id=user_id, movie_id=movie_id, direction=direction)
