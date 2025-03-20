from typing import Protocol, Optional

from domain.models.movie import Movie


class IMovieRepository(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[Movie]:
        ...

    def search(self, search_term: str) -> Optional[list[Movie]]:
        ...