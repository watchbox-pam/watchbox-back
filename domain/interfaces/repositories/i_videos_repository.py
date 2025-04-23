from typing import Protocol, Optional

from domain.models.videos import Videos


class IVideosRepository(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[Videos]:
        ...