from typing import Protocol

from domain.models.country import Country


class ICountryService(Protocol):
    def find_all_countries(self) -> list[Country]:
        ...