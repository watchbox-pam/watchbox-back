from typing import List, Dict, Any, Optional

from domain.interfaces.repositories.i_search_repository import ISearchRepository
from domain.interfaces.services.i_search_service import ISearchService

class SearchService(ISearchService):
    def __init__(self, repository: ISearchRepository):
        self.repository = repository

    def search_all(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        return self.repository.search_all(search_term, providers, include_adult)

    def search_movies(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> List[Dict[str, Any]]:
        return self.repository.search_movies(search_term, providers, include_adult)

    def search_actors(self, search_term: str, include_adult: bool = False) -> List[Dict[str, Any]]:
        return self.repository.search_actors(search_term, include_adult)

    def get_suggestions(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False):
        return self.repository.search_suggestions(search_term, providers, include_adult)
