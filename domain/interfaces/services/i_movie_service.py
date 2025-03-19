from typing import Protocol, Optional

from domain.models.movie import Movie, PopularMovieList

class IMovieService(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[Movie]:
        ...

    def find_by_time_window(self, time_window: str, page: int) -> Optional[PopularMovieList]:
        ...