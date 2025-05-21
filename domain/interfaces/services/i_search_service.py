from typing import Protocol, List, Optional, Dict, Any

class ISearchService(Protocol):
    def search_all(self, search_term: str, providers: Optional[List[int]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for movies, TV shows, and people matching the search term and optional provider filters
        """
        ...

    def search_movies(self, search_term: str, providers: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Search only for movies matching the search term and optional provider filters
        """
        ...

    def search_actors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for actors/people matching the search term
        """
        ...