from typing import List, Protocol, Optional

class ITVService(Protocol):
    def find_by_id(self, tv_id: int) -> Optional[dict]:
        ...

    