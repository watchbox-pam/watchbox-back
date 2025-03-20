from typing import Protocol, Optional

from domain.models.videos import Videos


class IVideosService(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[Videos]:
        ...