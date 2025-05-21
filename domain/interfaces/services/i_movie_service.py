from typing import Protocol, Optional

from domain.models.movie import Movie, PopularMovieList, MovieDetail
<<<<<<< HEAD
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movie_list_item import MovieListItem
=======
>>>>>>> develop


class IMovieService(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[MovieDetail]:
        ...

    def search(self, search_term: str) -> Optional[list[Movie]]:
        ...

    def find_by_time_window(self, time_window: str, page: int) -> Optional[PopularMovieList]:
        ...

<<<<<<< HEAD
    def get_random_movies(self, count: int = 3) -> Optional[List[MovieListItem]]:
        ...
=======
    def find_by_genre(self, genre: str) -> Optional[PopularMovieList]:
>>>>>>> develop
        ...