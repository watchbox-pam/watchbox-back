from typing import Protocol

from domain.models.country import Country as CountryList


class ICountryService(Protocol):
    def find_all_countries(self) -> list[CountryList]:
        ...