from typing import Protocol, List, Optional, Dict, Any

class ISearchService(Protocol):
    def search_all(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        ...

    def search_movies(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> List[Dict[str, Any]]:
        ...

    def search_actors(self, search_term: str, include_adult: bool = False) -> List[Dict[str, Any]]:
        ...

    def get_suggestions(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> List[Dict[str, Any]]:
        ...
