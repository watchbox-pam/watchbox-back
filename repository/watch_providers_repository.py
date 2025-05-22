from typing import Optional

from domain.interfaces.repositories.i_watch_providers_repository import IWatchProvidersRepository
from domain.models.watch_providers import WatchProviders
from utils.tmdb_service import call_tmdb_api


class WatchProvidersRepository(IWatchProvidersRepository):
    def find_by_id(self, movie_id: int) -> Optional[WatchProviders]:
        endpoint = f"/movie/{movie_id}/watch/providers"

        result = call_tmdb_api(endpoint)

        providers = WatchProviders(
            id=result["id"],
            results=result["results"]
        )

        return providers