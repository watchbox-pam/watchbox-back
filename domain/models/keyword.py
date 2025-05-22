from dataclasses import dataclass


@dataclass(frozen=True)
class Keyword:
    id: int
    name: str