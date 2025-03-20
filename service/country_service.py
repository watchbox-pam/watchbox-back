from domain.interfaces.repositories.i_country_repository import ICountryRepository
from domain.interfaces.services.i_country_service import ICountryService
from domain.models.country import Country


class CountryService(ICountryService):
    def __init__(self, repository: ICountryRepository):
        self.repository = repository

    def find_all_countries(self) -> list[Country]:
        countries = self.repository.find_all_countries()
        return countries