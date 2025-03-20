from fastapi import APIRouter
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.interfaces.services.i_movie_service import IMovieService
from repository.movie_repository import MovieRepository
from service.movie_service import MovieService

movie_router = APIRouter(prefix="/movies", tags=["Movies"])

def get_movie_service() -> IMovieService:
    repository: IMovieRepository = MovieRepository()
    return MovieService(repository)

@movie_router.get("/{movie_id}")
async def get_movie_by_id(movie_id: int, service: IMovieService = Depends(get_movie_service)):
    """
    Returns the details for a movie based on the movie id
    :param movie_id: the movie id to get
    :param service: the service to call to get the info
    :return: the details of the movie / or a 404 error if the id does not exist
    """
    movie = service.find_by_id(movie_id)
    if movie:
        return movie
    else:
        raise HTTPException(status_code=404, detail="Movie not found")


@movie_router.get("/search/{search}")
async def search_movies(search: str, service: IMovieService = Depends(get_movie_service)):
    movies = service.search(search)
    if movies:
        return movies
    else:
        raise HTTPException(status_code=404, detail="Movies not found")


@movie_router.get("/popular/{time_window}")
async def get_movie_by_time_window(time_window: str, page: int = 1, service: IMovieService = Depends(get_movie_service)):
    """
    Returns the details for a movie based on the movie id
    :param movie_id: the movie id to get
    :param service: the service to call to get the info
    :return: the details of the movie / or a 404 error if the id does not exist
    """
    movies = service.find_by_time_window(time_window, page)
    if movies:
        return movies
    else:
        raise HTTPException(status_code=404, detail="Movies not found")