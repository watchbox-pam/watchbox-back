from fastapi import APIRouter
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.i_movie_repository import IMovieRepository
from domain.interfaces.i_movie_service import IMovieService
from repository.movie_repository import MovieRepository
from service.movie_service import MovieService

movie_router = APIRouter(prefix="/movies", tags=["Movies"])

def get_movie_service() -> IMovieService:
    repository: IMovieRepository = MovieRepository()
    return MovieService(repository)

@movie_router.get("/{movie_id}")
async def get_movie_by_id(movie_id: str, service: IMovieService = Depends(get_movie_service)):
    movie = service.find_by_id(movie_id)
    if movie:
        return movie
    else:
        raise HTTPException(status_code=404, detail="Movie not found")