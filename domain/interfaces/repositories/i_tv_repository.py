from typing import Protocol, Optional, List
from domain.models.tv import Tv


class ITvRepository(Protocol):
    def find_by_id(self, tv_id: int) -> Optional[Tv]:
        ...
