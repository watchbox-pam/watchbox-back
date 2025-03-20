from typing import Protocol, Optional

from domain.models.credits import Credits


class ICreditsRepository(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[Credits]:
        ...