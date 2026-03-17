from typing import List, Protocol, Optional
from domain.models.tv import Tv

class ITVService(Protocol):
    def find_by_id(self, tv_id: int) -> Optional[Tv]:
        ...