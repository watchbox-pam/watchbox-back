from typing import Any, Dict, List, Protocol


class IOnboardingMovieRepository(Protocol):
    def get_candidates(self, user_id: str, include_adult: bool, provider_ids: List[int], pool_size: int) -> List[Dict[str, Any]]:
        """
        Films populaires que l'utilisateur n'a pas encore jugés.
        Chaque élément : id, title, poster_path, popularity, genre_ids, available
        (available = disponible en France sur une des plateformes de l'utilisateur).
        """
        ...
