from typing import Optional

from domain.interfaces.i_movie_repository import IMovieRepository
from domain.models.release_dates import ReleaseDates
from utils.tmdb_service import call_tmdb_api
from domain.interfaces.i_release_dates_repository import IReleaseDatesRepository


class ReleaseDateRepository(IReleaseDatesRepository):
    def find_by_id(self, movie_id: int) -> Optional[ReleaseDates]:
        endpoint = f"/movie/{movie_id}/release_dates"

        result = call_tmdb_api(endpoint)


        release_dates = ReleaseDates(
            id=result["id"],
            results=result["results"]
        )

        return release_dates