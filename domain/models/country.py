from dataclasses import dataclass


@dataclass(frozen=True)
class Country:
    iso: str
    name: str