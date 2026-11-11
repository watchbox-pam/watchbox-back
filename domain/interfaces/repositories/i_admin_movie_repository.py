from typing import Optional, Protocol

from database.models import Movie as DBMovie


class IAdminMovieRepository(Protocol):
    def count(self) -> int:
        ...

    def find_page(self, offset: int, limit: int) -> list[DBMovie]:
        ...

    def find_by_id(self, movie_id: int) -> Optional[DBMovie]:
        ...

    def create(self, data: dict) -> DBMovie:
        ...

    def update(self, movie_id: int, data: dict) -> Optional[DBMovie]:
        ...

    def delete(self, movie_id: int) -> bool:
        ...
