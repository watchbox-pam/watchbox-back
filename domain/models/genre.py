from dataclasses import dataclass


@dataclass(frozen=True)
class Genre:
    id: int
    name: str