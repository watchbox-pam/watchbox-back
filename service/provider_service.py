from typing import List, Dict, Any

from domain.interfaces.repositories.i_provider_repository import IProviderRepository
from domain.interfaces.services.i_provider_service import IProviderService


class ProviderService(IProviderService):
    def __init__(self, repository: IProviderRepository):
        self.repository = repository

    def get_providers(self) -> List[Dict[str, Any]]:
        """
        Get all available streaming providers from TMDB
        """
        return self.repository.get_providers()

    def get_movie_providers(self, movie_id: int) -> List[Dict[str, Any]]:
        """
        Get streaming providers for a specific movie
        """
        return self.repository.get_movie_providers(movie_id)