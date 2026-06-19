from typing import Protocol, List, Optional, Dict, Any

from domain.models.user import UserSearchResult


class ISearchRepository(Protocol):
    def search_all(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        ...

    def search_movies(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> List[Dict[str, Any]]:
        ...

    def search_actors(self, search_term: str, include_adult: bool = False) -> List[Dict[str, Any]]:
        ...

    def search_users(self, search_term: str) -> List[UserSearchResult]:
        ...

    def search_suggestions(self, search_term: str, providers: Optional[List[int]] = None, include_adult: bool = False) -> List[Dict[str, Any]]:
        ...
