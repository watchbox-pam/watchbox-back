from typing import Protocol, Optional

from domain.models.person import PersonDetail

class IPersonService(Protocol):
    def find_by_id(self, movie_id: int) -> Optional[PersonDetail]:
        ...