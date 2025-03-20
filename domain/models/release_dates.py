from dataclasses import dataclass

class ReleaseDate:
    certification: str
    descriptors: list
    iso_639_1: str
    note: str
    release_date: str
    type: int

class Results:
    iso_3166_1: str
    release_dates: list[ReleaseDate]


@dataclass(frozen=True)
class ReleaseDates:
    id: int
    results: list[Results]
