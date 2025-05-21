from typing import Protocol, Optional, List

from domain.models.movie import Movie, PopularMovieList, MovieDetail, MovieId
from domain.models.movieRecommendation import MovieRecommendation


class IMovieRepository(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[MovieDetail]:
        ...

    def search(self, search_term: str) -> Optional[list[Movie]]:
        ...

    def find_by_time_window(self, time_window: str, page: int) -> Optional[PopularMovieList]:
        ...

    def movie_runtime(self, movie_ids: List[int]) -> int:
        ...