import statistics
import os
from typing import List

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING
from domain.models.movieReview import MovieReview
from service.ml_service import MLService


class RecommendationService(IRecommendationService):
    def __init__(self, repository: IRecommendationRepository, playlist_repository: IPlaylistRepository):
        self.repository = repository
        self.playlist_repository = playlist_repository
        self.ml: MLService | None = None
        if os.path.exists("ml_model.pkl"):
            try:
                self.ml = MLService.load("ml_model.pkl")
            except:
                self.ml = None

    def _get_adaptive_weights(self, user_id: str, rating_count: int) -> tuple:
        if not self.ml or not self.ml.is_trained:
            return (0.0, 0.0, 1.0)
        user_known = user_id in self.ml.user_index
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
        no_ml = not self.ml or user_id not in self.ml.user_index
        no_playlists = not watchlist_ids and not history_ids and not favorites_ids
        return no_ml and no_playlists

    def _get_cold_start_recommendations(self, emotion: Emotion, limit: int = 10) -> List[MovieRecommendation]:
        genre_medias = self.repository.find_by_genres(EMOTION_GENRE_MAPPING[emotion])
        for media in genre_medias:
            media.weight = media.popularity
        genre_medias = sorted(genre_medias, key=lambda x: x.weight, reverse=True)
        return self._diversify(genre_medias[:50], top_n=limit, diversity_penalty=0.6)[:limit]

    def get_recommendations(
        self,
        emotion: Emotion,
        user_id: str,
        limit: int = 10,
        exclude_ids: list[int] | None = None
    ):
        if limit < 1:
            limit = 1
        if limit > 50:
            limit = 50

        exclude_set = set(exclude_ids or [])

        user_playlists = self.playlist_repository.get_playlists_by_user_id(user_id)
        user_watchlist_id = user_history_id = user_favorites_id = ""

        for item in user_playlists:
            if item.title == "Watchlist":
                user_watchlist_id = str(item.id)
            if item.title == "Historique":
                user_history_id = str(item.id)
            if item.title == "Favoris":
                user_favorites_id = str(item.id)

        user_watchlist = self.playlist_repository.get_playlist_medias(user_watchlist_id) or []
        user_history = self.playlist_repository.get_playlist_medias(user_history_id) or []
        user_favorites = self.playlist_repository.get_playlist_medias(user_favorites_id) or []

        watchlist_ids = [m.movie_id for m in user_watchlist]
        history_ids = [m.movie_id for m in user_history]
        favorites_ids = [m.movie_id for m in user_favorites]

        if self._is_cold_start(user_id, watchlist_ids, history_ids, favorites_ids):
            print(f"Cold start détecté pour user {user_id}")
            return self._get_cold_start_recommendations(emotion, limit=limit)

        keywords, actors, directors = [], [], []

        if watchlist_ids:
            for media in self.repository.find_by_ids_recommendation(watchlist_ids):
                for kw in media.keywords:
                    keywords.append({"value": kw, "weight": 10})
                for c in media.credits:
                    if c["job_id"] == "96":
                        actors.append({"value": c["person_id"], "weight": 10})
                    elif c["job_id"] == "537":
                        directors.append({"value": c["person_id"], "weight": 10})

        if history_ids:
            history_reviews: List[MovieReview] = self.repository.find_with_review(user_id, history_ids)
            for media in self.repository.find_by_ids_recommendation(history_ids):
                ratings = [r.rating for r in history_reviews if r.movie_id == media.id]
                w = (statistics.fmean(ratings) - 5) if ratings else 0
                for kw in media.keywords:
                    keywords.append({"value": kw, "weight": w})
                for c in media.credits:
                    if c["job_id"] == "96":
                        actors.append({"value": c["person_id"], "weight": w})
                    elif c["job_id"] == "537":
                        directors.append({"value": c["person_id"], "weight": w})

        if favorites_ids:
            for media in self.repository.find_by_ids_recommendation(favorites_ids):
                for kw in media.keywords:
                    keywords.append({"value": kw, "weight": 20})
                for c in media.credits:
                    if c["job_id"] == "96":
                        actors.append({"value": c["person_id"], "weight": 20})
                    elif c["job_id"] == "537":
                        directors.append({"value": c["person_id"], "weight": 20})

        genre_medias = self.repository.find_by_genres(EMOTION_GENRE_MAPPING[emotion])

        # Exclure historique + exclude_ids
        history_set = set(history_ids)
        if history_set or exclude_set:
            genre_medias = [
                m for m in genre_medias
                if (m.id not in history_set and m.id not in exclude_set)
            ]

        candidate_ids = [m.id for m in genre_medias]

        if not genre_medias:
            return self._get_cold_start_recommendations(emotion, limit=limit)

        for media in genre_medias:
            media.weight = len(media.genres)

            if media.id in watchlist_ids:
                media.weight += 10
            for kw in media.keywords:
                for k in filter(lambda x: x["value"] == kw, keywords):
                    media.weight += k["weight"]
            for c in media.credits:
                if c["job_id"] == "96":
                    for a in filter(lambda x: x["value"] == c["person_id"], actors):
                        media.weight += a["weight"]
                elif c["job_id"] == "537":
                    for d in filter(lambda x: x["value"] == c["person_id"], directors):
                        media.weight += d["weight"] * 2

        rating_count = len(history_ids)
        w_svd, w_als, w_content = self._get_adaptive_weights(user_id, rating_count)

        content_scores = self._normalize(genre_medias)
        svd_scores = {}
        als_scores = {}

        if self.ml and self.ml.is_trained:
            svd_scores = {mid: self.ml.predict_svd(user_id, mid) for mid in candidate_ids}
            als_scores = self.ml.predict_als(user_id, candidate_ids)

        for media in genre_medias:
            media.weight = (
                svd_scores.get(media.id, 0.0) * w_svd
                + als_scores.get(media.id, 0.0) * w_als
                + content_scores.get(media.id, 0.0) * w_content
            )

        genre_medias = sorted(genre_medias, key=lambda x: x.popularity, reverse=True)
        genre_medias = sorted(genre_medias, key=lambda x: x.weight, reverse=True)

        pool_size = max(30, limit * 3)
        diversified = self._diversify(genre_medias[:pool_size], top_n=limit, diversity_penalty=0.3)
        return diversified[:limit]