from typing import Protocol, List, Dict, Any

class IProviderService(Protocol):
    def get_providers(self) -> List[Dict[str, Any]]:
        """
        Get all available streaming providers from TMDB
        """
        ...

    def get_movie_providers(self, movie_id: int) -> List[Dict[str, Any]]:
        """
        Get streaming providers for a specific movie
        """
        ...