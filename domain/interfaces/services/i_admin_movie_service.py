from typing import Protocol

from domain.models.admin_movie import AdminMovieCreate, AdminMovieUpdate


class IAdminMovieService(Protocol):
    def get_movies(self, page: int, limit: int) -> dict:
        ...

    def get_movie(self, movie_id: int) -> dict:
        ...

    def create_movie(self, data: AdminMovieCreate) -> dict:
        ...

    def update_movie(self, movie_id: int, data: AdminMovieUpdate) -> dict:
        ...

    def delete_movie(self, movie_id: int) -> dict:
        ...
