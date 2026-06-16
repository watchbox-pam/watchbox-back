import statistics
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import List

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING
from domain.models.movieReview import MovieReview
from service.ml_state import get_ml

SKIP_PENALTY = 0.5


class RecommendationService(IRecommendationService):
    def __init__(self, repository: IRecommendationRepository, playlist_repository: IPlaylistRepository):
        self.repository = repository
        self.playlist_repository = playlist_repository

    def _get_adaptive_weights(self, user_id: str, rating_count: int) -> tuple:
        ml = get_ml()
        if not ml or not ml.is_trained:
            return (0.0, 0.0, 1.0)
        user_known = user_id in ml.user_index
        if not user_known or rating_count < 5:
            return (0.05, 0.15, 0.80)
        elif rating_count < 20:
            return (0.30, 0.30, 0.40)
        else:
            return (0.45, 0.35, 0.20)

    def _normalize(self, medias: List[MovieRecommendation]) -> dict:
        if not medias:
            return {}
        weights = [m.weight for m in medias]
        max_w, min_w = max(weights), min(weights)
        if max_w == min_w:
            return {m.id: 1.0 for m in medias}
        return {m.id: (m.weight - min_w) / (max_w - min_w) for m in medias}

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _diversify(
        self,
        medias: List[MovieRecommendation],
        top_n: int = 10,
        diversity_penalty: float = 0.3
    ) -> List[MovieRecommendation]:
        if not medias:
            return []
        features = {m.id: set(m.keywords) | set(m.genres) for m in medias}
        selected = []
        candidates = list(medias)
        while len(selected) < top_n and candidates:
            best = None
            best_score = -1
            for candidate in candidates:
                score = candidate.weight
                if selected:
                    max_similarity = max(
                        self._jaccard_similarity(features[candidate.id], features[s.id])
                        for s in selected
                    )
                    score = score * (1 - diversity_penalty * max_similarity)
                if score > best_score:
                    best_score = score
                    best = candidate
            if best:
                selected.append(best)
                candidates.remove(best)
        return selected

    def _is_cold_start(self, user_id: str, watchlist_ids: list, history_ids: list, favorites_ids: list) -> bool:
        ml = get_ml()
        no_ml = not ml or user_id not in ml.user_index
        no_playlists = not watchlist_ids and not history_ids and not favorites_ids
        return no_ml and no_playlists

    def _get_cold_start_recommendations(self, emotion: Emotion, limit: int = 10, include_adult: bool = False) -> List[MovieRecommendation]:
        genre_medias = self.repository.find_by_genres(EMOTION_GENRE_MAPPING[emotion], include_adult)
        for media in genre_medias:
            media.weight = media.popularity
        genre_medias = sorted(genre_medias, key=lambda x: x.weight, reverse=True)
        return self._diversify(genre_medias[:50], top_n=limit, diversity_penalty=0.6)[:limit]

    def get_recommendations(
        self,
        emotion: Emotion,
        user_id: str,
        limit: int = 10,
        exclude_ids: list[int] | None = None,
        include_adult: bool = False
    ):
        if limit < 1:
            limit = 1
        if limit > 50:
            limit = 50

        # Phase 1 : toutes les requêtes indépendantes en parallèle
        with ThreadPoolExecutor() as ex:
            f_skip      = ex.submit(self.repository.get_skip_movie_ids, user_id)
            f_playlists = ex.submit(self.playlist_repository.get_playlists_by_user_id, user_id)
            f_swipes    = ex.submit(self.repository.get_swipe_movie_ids, user_id)
            f_genres    = ex.submit(self.repository.find_by_genres, EMOTION_GENRE_MAPPING[emotion], include_adult)

        skip_ids       = f_skip.result()
        user_playlists = f_playlists.result()
        swipe_ids      = f_swipes.result()
        genre_medias   = f_genres.result()

        skip_set = set(skip_ids)
        exclude_set = set(exclude_ids or [])

        user_watchlist_id = user_history_id = user_favorites_id = ""
        for item in user_playlists:
            if item.title == "Watchlist":
                user_watchlist_id = str(item.id)
            if item.title == "Historique":
                user_history_id = str(item.id)
            if item.title == "Favoris":
                user_favorites_id = str(item.id)

        # Phase 2 : contenu des playlists en parallèle
        with ThreadPoolExecutor() as ex:
            f_watchlist  = ex.submit(self.playlist_repository.get_playlist_medias, user_watchlist_id)
            f_history    = ex.submit(self.playlist_repository.get_playlist_medias, user_history_id)
            f_favorites  = ex.submit(self.playlist_repository.get_playlist_medias, user_favorites_id)

        user_watchlist = f_watchlist.result() or []
        user_history   = f_history.result()   or []
        user_favorites = f_favorites.result() or []

        watchlist_ids       = [m.movie_id for m in user_watchlist]
        playlist_history_ids = [m.movie_id for m in user_history]
        history_ids         = list(dict.fromkeys(playlist_history_ids + swipe_ids))
        favorites_ids       = [m.movie_id for m in user_favorites]

        if self._is_cold_start(user_id, watchlist_ids, history_ids, favorites_ids):
            print(f"Cold start détecté pour user {user_id}")
            return self._get_cold_start_recommendations(emotion, limit=limit, include_adult=include_adult)

        # Phase 3 : données de contenu en parallèle
        with ThreadPoolExecutor() as ex:
            f_wl_reco   = ex.submit(self.repository.find_by_ids_recommendation, watchlist_ids) if watchlist_ids else None
            f_hist_reco = ex.submit(self.repository.find_by_ids_recommendation, history_ids)   if history_ids  else None
            f_fav_reco  = ex.submit(self.repository.find_by_ids_recommendation, favorites_ids) if favorites_ids else None
            f_reviews   = ex.submit(self.repository.find_with_review, user_id, history_ids)    if history_ids  else None

        kw_weights: dict = defaultdict(float)
        actor_weights: dict = defaultdict(float)
        director_weights: dict = defaultdict(float)

        if watchlist_ids and f_wl_reco:
            for media in f_wl_reco.result():
                for kw in media.keywords:
                    kw_weights[kw] += 10
                for c in media.credits:
                    if c["job_id"] == 96:
                        actor_weights[c["person_id"]] += 10
                    elif c["job_id"] == 537:
                        director_weights[c["person_id"]] += 10

        rating_count = 0
        if history_ids and f_hist_reco:
            history_reviews: List[MovieReview] = f_reviews.result() if f_reviews else []
            rating_count = len(history_reviews)
            review_map = defaultdict(list)
            for r in history_reviews:
                review_map[r.movie_id].append(r.rating)
            for media in f_hist_reco.result():
                ratings = review_map[media.id]
                w = (statistics.fmean(ratings) - 5) if ratings else 0
                for kw in media.keywords:
                    kw_weights[kw] += w
                for c in media.credits:
                    if c["job_id"] == 96:
                        actor_weights[c["person_id"]] += w
                    elif c["job_id"] == 537:
                        director_weights[c["person_id"]] += w

        if favorites_ids and f_fav_reco:
            for media in f_fav_reco.result():
                for kw in media.keywords:
                    kw_weights[kw] += 10
                for c in media.credits:
                    if c["job_id"] == 96:
                        actor_weights[c["person_id"]] += 10
                    elif c["job_id"] == 537:
                        director_weights[c["person_id"]] += 10

        seen_set = set(history_ids) | set(favorites_ids) | exclude_set
        if seen_set:
            genre_medias = [m for m in genre_medias if m.id not in seen_set]

        candidate_ids = [m.id for m in genre_medias]

        if not genre_medias:
            return self._get_cold_start_recommendations(emotion, limit=limit, include_adult=include_adult)

        watchlist_set = set(watchlist_ids)
        for media in genre_medias:
            media.weight = len(media.genres)
            if media.id in watchlist_set:
                media.weight += 10
            for kw in media.keywords:
                media.weight += kw_weights.get(kw, 0)
            for c in media.credits:
                if c["job_id"] == 96:
                    media.weight += actor_weights.get(c["person_id"], 0)
                elif c["job_id"] == 537:
                    media.weight += director_weights.get(c["person_id"], 0) * 2

        w_svd, w_als, w_content = self._get_adaptive_weights(user_id, rating_count)

        content_scores = self._normalize(genre_medias)
        svd_scores = {}
        als_scores = {}

        ml = get_ml()
        if ml and ml.is_trained:
            svd_scores = ml.predict_svd_batch(user_id, candidate_ids)
            als_scores = ml.predict_als(user_id, candidate_ids)

        for media in genre_medias:
            media.weight = (
                svd_scores.get(media.id, 0.0) * w_svd
                + als_scores.get(media.id, 0.0) * w_als
                + content_scores.get(media.id, 0.0) * w_content
            )
            if media.id in skip_set:
                media.weight *= SKIP_PENALTY

        genre_medias = sorted(genre_medias, key=lambda x: x.popularity, reverse=True)
        genre_medias = sorted(genre_medias, key=lambda x: x.weight, reverse=True)

        pool_size = max(30, limit * 3)
        diversified = self._diversify(genre_medias[:pool_size], top_n=limit, diversity_penalty=0.5)
        return diversified[:limit]