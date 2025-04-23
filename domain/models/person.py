from datetime import date
from dataclasses import dataclass

@dataclass(frozen=True)
class PersonDetail:
    id: int
    adult: bool
    also_known_as: list[str]
    biography: str
    birthday: str
    deathday: str
    gender: int
    homepage: str
    imdb_id: str
    known_for_department: str
    name: str
    place_of_birth: str
    popularity: int
    profile_path: str