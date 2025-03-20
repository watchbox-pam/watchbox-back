from typing import Protocol, Optional

from domain.models.release_dates import ReleaseDates


class IReleaseDatesService(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[ReleaseDates]:
        ...