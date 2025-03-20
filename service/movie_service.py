from typing import Optional

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.interfaces.services.i_movie_service import IMovieService
from domain.models.movie import Movie


class MovieService(IMovieService):
    def __init__(self, repository: IMovieRepository):
        self.repository = repository

    def find_by_id(self, movie_id: int) -> Optional[Movie]:
        movie = self.repository.find_by_id(movie_id)
        return movie


    def search(self, search_term: str) -> Optional[list[Movie]]:
        return self.repository.search(search_term)

    def find_by_time_window(self, time_window: str, page: int) -> Optional[Movie]:
            movie = self.repository.find_by_time_window(time_window, page)
            return movie