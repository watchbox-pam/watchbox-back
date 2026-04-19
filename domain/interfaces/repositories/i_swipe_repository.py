from typing import Protocol


class ISwipeRepository(Protocol):
    def create_swipe(self, user_id: str, movie_id: int, direction: str) -> dict:
        ...
