from database.models import Movie as DBMovie
from domain.interfaces.repositories.i_admin_movie_repository import IAdminMovieRepository
from domain.interfaces.services.i_admin_movie_service import IAdminMovieService
from domain.models.admin_errors import AdminConflictError, AdminNotFoundError
from domain.models.admin_movie import AdminMovieCreate, AdminMovieUpdate


def _movie_to_dict(movie: DBMovie) -> dict:
    return {
        "id": movie.id,
        "title": movie.title,
        "poster_path": movie.poster_path,
        "release_date": (
            movie.release_date.isoformat()
            if movie.release_date
            else None
        ),
        "popularity": movie.popularity,
        "runtime": movie.runtime,
        "infos_complete": movie.infos_complete,
        "adult": movie.adult,
    }


class AdminMovieService(IAdminMovieService):
    def __init__(self, repository: IAdminMovieRepository):
        self.repository = repository

    def get_movies(self, page: int, limit: int) -> dict:
        offset = (page - 1) * limit

        total = self.repository.count()
        movies = self.repository.find_page(offset, limit)

        return {
            "items": [_movie_to_dict(movie) for movie in movies],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit,
            },
        }

    def get_movie(self, movie_id: int) -> dict:
        movie = self.repository.find_by_id(movie_id)

        if not movie:
            raise AdminNotFoundError("Film introuvable")

        return _movie_to_dict(movie)

    def create_movie(self, data: AdminMovieCreate) -> dict:
        if self.repository.find_by_id(data.id):
            raise AdminConflictError("Un film avec cet ID existe déjà")

        movie = self.repository.create(data.model_dump())

        return _movie_to_dict(movie)

    def update_movie(self, movie_id: int, data: AdminMovieUpdate) -> dict:
        movie = self.repository.update(
            movie_id,
            data.model_dump(exclude_unset=True)
        )

        if not movie:
            raise AdminNotFoundError("Film introuvable")

        return _movie_to_dict(movie)

    def delete_movie(self, movie_id: int) -> dict:
        if not self.repository.delete(movie_id):
            raise AdminNotFoundError("Film introuvable")

        return {
            "success": True,
            "id": movie_id
        }
