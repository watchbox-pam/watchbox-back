from typing import Protocol, Optional

from domain.models.credits import Credits


class ICreditsService(Protocol):
    def find_by_id(self, movie_id: int, include_adult: bool) -> Optional[Credits]:
        ...