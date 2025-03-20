from typing import Optional

from domain.interfaces.i_videos_repository import IVideosRepository
from domain.models.videos import Videos
from utils.tmdb_service import call_tmdb_api


class VideosRepository(IVideosRepository):
    def find_by_id(self, movie_id: int) -> Optional[Videos]:
        endpoint = f"/movie/{movie_id}/videos"

        result = call_tmdb_api(endpoint)

        videos = Videos(
            id=result["id"],
            results=result["results"]
        )

        return videos