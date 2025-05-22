from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from domain.interfaces.services.i_provider_service import IProviderService
from service.provider_service import ProviderService
from repository.provider_repository import ProviderRepository

provider_router = APIRouter(prefix="/providers", tags=["Providers"])

def get_provider_service() -> IProviderService:
    repository = ProviderRepository()
    return ProviderService(repository)

@provider_router.get("/")
async def get_providers(service: IProviderService = Depends(get_provider_service)) -> List[Dict[str, Any]]:
    """
    Get all available streaming providers from TMDB
    """
    return service.get_providers()

@provider_router.get("/movie/{movie_id}")
async def get_movie_providers(movie_id: int, service: IProviderService = Depends(get_provider_service)) -> List[Dict[str, Any]]:
    """
    Get streaming providers for a specific movie
    """
    return service.get_movie_providers(movie_id)