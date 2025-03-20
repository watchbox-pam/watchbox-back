from typing import Protocol, Optional

from domain.models.watch_providers import WatchProviders


class IWatchProvidersService(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[WatchProviders]:
        ...