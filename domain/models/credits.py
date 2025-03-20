from dataclasses import dataclass

@dataclass
class Cast:
    adult: bool
    gender: int
    id: int
    known_for_department: str
    name: str
    original_name: str
    popularity: int
    profile_path: str
    cast_id: int
    character: str
    credit_id: str
    order: int

@dataclass
class Crew:
    adult: bool
    gender: int
    id: int
    known_for_department: str
    name: str
    original_name: str
    popularity: int
    profile_path: str
    credit_id: str
    department: int
    job: str

@dataclass(frozen=True)
class Credits:
    id: int
    cast: list[Cast]
    crew: list[Crew]
    