import random
from collections import Counter
from typing import Any, Dict, List, Optional

from domain.interfaces.repositories.i_onboarding_movie_repository import IOnboardingMovieRepository
from domain.interfaces.repositories.i_user_provider_repository import IUserProviderRepository
from domain.models.movie_list_item import MovieListItem


class OnboardingMovieService:
    """Sélection des films proposés au swipe d'onboarding."""

    POOL_SIZE = 200        # on pioche parmi les films les plus populaires
    MAX_PER_GENRE = 3      # au-delà, un genre est jugé « plein » pour la première passe

    def __init__(self, repository: IOnboardingMovieRepository, user_provider_repository: IUserProviderRepository,
                 rng: Optional[random.Random] = None):
        self.repository = repository
        self.user_provider_repository = user_provider_repository
        self.rng = rng or random.Random()

    def get_onboarding_movies(self, user_id: str, count: int, include_adult: bool) -> List[MovieListItem]:
        provider_ids = [p["id"] for p in self.user_provider_repository.get_user_providers(user_id)]
        candidates = self.repository.get_candidates(user_id, include_adult, provider_ids, self.POOL_SIZE)
        picked = self.select_movies(candidates, count)
        return [MovieListItem(id=c["id"], title=c["title"], poster_path=c["poster_path"]) for c in picked]

    def select_movies(self, candidates: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        # 1. Films dispo sur les plateformes de l'utilisateur d'abord, puis les autres.
        #    Mélangés dans chaque groupe pour que chacun n'ait pas exactement les mêmes 15 films.
        available = [c for c in candidates if c.get("available")]
        others = [c for c in candidates if not c.get("available")]
        self.rng.shuffle(available)
        self.rng.shuffle(others)
        ordered = available + others

        # 2. Première passe : diversité des genres (plus de signal pour la recommandation)
        picked: List[Dict[str, Any]] = []
        per_genre: Counter = Counter()
        for candidate in ordered:
            if len(picked) >= count:
                break
            genres = candidate.get("genre_ids") or []
            if any(per_genre[g] >= self.MAX_PER_GENRE for g in genres):
                continue
            picked.append(candidate)
            per_genre.update(genres)

        # 3. Si la diversité ne suffit pas à remplir, on complète sans contrainte
        if len(picked) < count:
            picked_ids = {c["id"] for c in picked}
            picked += [c for c in ordered if c["id"] not in picked_ids][:count - len(picked)]

        self.rng.shuffle(picked)
        return picked
