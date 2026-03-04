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


tv_router = APIRouter(prefix="/tv", tags=["Tv"])

@tv_router.get("/id/{tv_id}")
async def get_tv_by_id(tv_id: int, service):
    """
    Returns the details for a TV show based on the TV show id
    :param tv_id: the TV show id to get
    """

    tv = service.find_by_id(tv_id)
    if tv:
        return tv
    else:        
        raise HTTPException(status_code=404, detail="TV show not found")
