from fastapi import APIRouter
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.interfaces.services.i_movie_service import IMovieService
from repository.movie_repository import MovieRepository
from service.movie_service import MovieService
from repository.release_dates_repository import ReleaseDateRepository
from domain.interfaces.repositories.i_release_dates_repository import IReleaseDatesRepository
from repository.credits_repository import CreditsRepository
from domain.interfaces.repositories.i_credits_repository import ICreditsRepository
from repository.videos_repository import VideosRepository
from domain.interfaces.repositories.i_videos_repository import IVideosRepository
from repository.watch_providers_repository import WatchProvidersRepository
from domain.interfaces.repositories.i_watch_providers_repository import IWatchProvidersRepository

movie_router = APIRouter(prefix="/movies", tags=["Movies"])

def get_movie_service() -> IMovieService:
    repository: IMovieRepository = MovieRepository()
    release_dates_repository: IReleaseDatesRepository = ReleaseDateRepository()
    credits_repository: ICreditsRepository = CreditsRepository()
    videos_repository: IVideosRepository = VideosRepository()
    watch_providers_repository: IWatchProvidersRepository = WatchProvidersRepository()
    return MovieService(repository, release_dates_repository, credits_repository, videos_repository, watch_providers_repository)

@movie_router.get("/id/{movie_id}")
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
    if movies is not None:
        return movies
    else:
        raise HTTPException(status_code=404, detail="Movies not found")


@movie_router.get("/popular/{time_window}")
async def get_movie_by_time_window(time_window: str, page: int = 1, service: IMovieService = Depends(get_movie_service)):
    movies = service.find_by_time_window(time_window, page)
    if movies:
        return movies
    else:
        raise HTTPException(status_code=404, detail="Movies not found")

@movie_router.get("/random")
async def get_random_movies(
    count: int = 50,
    service: IMovieService = Depends(get_movie_service)
):
    print(f"count demandé : {count}")
    movies = service.get_random_movies(count)
    print(f"movies récupérés : {movies}")
    if movies:
        return movies
    else:
        raise HTTPException(status_code=404, detail="No movies found")

@movie_router.get("/genres/{genre}")
async def get_movie_by_genre(genre: str, service: IMovieService = Depends(get_movie_service)):
    movies = service.find_by_genre(genre)
    if movies:
        return movies
    else:
        raise HTTPException(status_code=404, detail="Movies not found")