from fastapi import APIRouter
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_country_repository import ICountryRepository
from domain.interfaces.services.i_country_service import ICountryService
from repository.country_repository import CountryRepository
from service.country_service import CountryService

country_router = APIRouter(prefix="/countries", tags=["Countries"])

def get_country_service() -> ICountryService:
    repository: ICountryRepository = CountryRepository()
    return CountryService(repository)

@country_router.get("")
async def get_all_countries(service: ICountryService = Depends(get_country_service)):
    countries = service.find_all_countries()
    if countries:
        return countries
    else:
        raise HTTPException(status_code=404, detail="Countries not found")