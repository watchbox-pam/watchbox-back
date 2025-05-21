from typing import Protocol, List, Optional, Dict, Any

class ISearchRepository(Protocol):
    def search_all(self, search_term: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for movies, TV shows, and people matching the search term
        """
        ...

    def search_movies(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for movies matching the search term
        """
        ...

    def search_actors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search only for actors/people matching the search term
        """
        ...