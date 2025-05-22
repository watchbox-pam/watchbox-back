from dataclasses import dataclass

@dataclass
class Video:
    iso_639_1: str
    iso_3166_1: str
    name: str
    key: str
    site: str
    size: int
    type: str
    official: bool
    published_at: str
    id: str


@dataclass(frozen=True)
class Videos:
    id: int
    results: list[Video]
