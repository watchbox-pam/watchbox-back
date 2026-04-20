from typing import Protocol, Optional

from domain.models.person import PersonDetail

class IPersonRepository(Protocol):
    def find_by_id(self, actor_id: int, include_adult: bool) -> Optional[PersonDetail]:
        ...