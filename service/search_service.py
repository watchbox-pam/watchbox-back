from typing import List, Dict, Any

from domain.interfaces.repositories.i_search_repository import ISearchRepository
from domain.interfaces.services.i_search_service import ISearchService

class SearchService(ISearchService):
    def __init__(self, repository: ISearchRepository):
        self.repository = repository

    def search_all(self, search_term: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for movies, TV shows, and people matching the search term
        """
        return self.repository.search_all(search_term)

    def search_movies(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for movies matching the search term
        """
        return self.repository.search_movies(search_term)

    def search_actors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for actors/people matching the search term
        """
        return self.repository.search_actors(search_term)
