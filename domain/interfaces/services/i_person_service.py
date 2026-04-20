from typing import Protocol, Optional

from domain.models.person import PersonDetail

class IPersonService(Protocol):
    def find_by_id(self, person_id: int, include_adult: bool) -> Optional[PersonDetail]:
        ...