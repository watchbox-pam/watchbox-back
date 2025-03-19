from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class MovieListItem:
    id: int
    title: str
    poster_path: Optional[str]