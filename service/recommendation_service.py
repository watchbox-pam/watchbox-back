from typing import List
import statistics

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING
from domain.models.movieReview import MovieReview


class RecommendationService(IRecommendationService):
    def __init__(self, repository: IRecommendationRepository, playlist_repository: IPlaylistRepository):
        self.repository = repository
        self.playlist_repository = playlist_repository


    def get_recommendations(self, emotion: Emotion, user_id: str):
        # Fetching user main playlists : Watchlist, History and Favorites
        user_playlists = self.playlist_repository.get_playlists_by_user_id(user_id)
        user_watchlist_id: str = ""
        user_history_id: str = ""
        user_favorites_id: str = ""
        playlist_ids_fetched: int = 0
        for item in user_playlists:
            if playlist_ids_fetched == 3:
                break
            if item.title == "Watchlist":
                user_watchlist_id = str(item.id)
                playlist_ids_fetched += 1
            if item.title == "Historique":
                user_history_id = str(item.id)
                playlist_ids_fetched += 1
            if item.title == "Favoris":
                user_favorites_id = str(item.id)
                playlist_ids_fetched += 1

        user_watchlist = self.playlist_repository.get_playlist_medias(user_watchlist_id)
        user_history = self.playlist_repository.get_playlist_medias(user_history_id)
        user_favorites = self.playlist_repository.get_playlist_medias(user_favorites_id)

        user_has_watchlist_content: bool = len(user_watchlist) > 0
        user_has_history_content: bool = len(user_history) > 0
        user_has_favorites_content: bool = len(user_favorites) > 0

        watchlist_media_ids = []
        if user_has_watchlist_content:
            for media in user_watchlist:
                watchlist_media_ids.append(media.movie_id)

        history_media_ids = []
        if user_has_history_content:
            for media in user_history:
                history_media_ids.append(media.movie_id)

        favorites_media_ids = []
        if user_has_favorites_content:
            for media in user_favorites:
                favorites_media_ids.append(media.movie_id)

        # Fetching infos of playlists
        if user_has_watchlist_content:
            watchlist_media_infos: List[MovieRecommendation] = self.repository.find_by_ids_recommendation(watchlist_media_ids)
        if user_has_history_content:
            history_media_infos: List[MovieRecommendation] = self.repository.find_by_ids_recommendation(history_media_ids)
        if user_has_favorites_content:
            favorites_media_infos: List[MovieRecommendation] = self.repository.find_by_ids_recommendation(favorites_media_ids)

        keywords = []
        actors = []
        directors = []

        # Adding data from the watchlist medias
        if user_has_watchlist_content:
            for watchlist_media in watchlist_media_infos:
                for keyword in watchlist_media.keywords:
                    keywords.append({ "value": keyword, "weight": 10 })
                for credit in watchlist_media.credits:
                    if credit["job_id"] == "96": # Job id for actors
                        actors.append({ "value": credit["person_id"], "weight": 10 })
                    elif credit["job_id"] == "537": # Job id for movie directors
                        directors.append({ "value": credit["person_id"], "weight": 10 })

        # Adding data from the history medias
        if user_has_history_content:
            history_movie_reviews: List[MovieReview] = self.repository.find_with_review(user_id, history_media_ids)
            print(history_movie_reviews)

            for history_media in history_media_infos:
                ratings: List[int] = []
                for r in history_movie_reviews:
                    if r.movie_id == history_media.id:
                        ratings.append(r.rating)
                media_weight = statistics.fmean(ratings)
                for keyword in history_media.keywords:
                    keywords.append({ "value": keyword, "weight": media_weight })
                for credit in history_media.credits:
                    if credit["job_id"] == "96":  # Job id for actors
                        actors.append({ "value": credit["person_id"], "weight": media_weight })
                    elif credit["job_id"] == "537":  # Job id for movie directors
                        directors.append({ "value": credit["person_id"], "weight": media_weight })

        # Adding data from the favorites medias
        if user_has_favorites_content:
            for favorites_media in favorites_media_infos:
                for keyword in favorites_media.keywords:
                    keywords.append({ "value": keyword, "weight": 20 })
                for credit in favorites_media.credits:
                    if credit["job_id"] == "96":  # Job id for actors
                        actors.append({ "value": credit["person_id"], "weight": 20})
                    elif credit["job_id"] == "537":  # Job id for movie directors
                        directors.append({"value": credit["person_id"], "weight": 20})

        # Getting medias matching selected emotion / genres
        genre_medias = self.repository.find_by_genres(EMOTION_GENRE_MAPPING[emotion])

        user_has_any_content: bool = user_has_watchlist_content or user_has_history_content or user_has_favorites_content
        for media in genre_medias:
            media.weight = len(media.genres)
            if user_has_any_content > 0:
                # Check if media is in the user watchlist
                if media.id in watchlist_media_ids:
                    media.weight += 10
                # Add weight based on the watchlist keywords
                for keyword in media.keywords:
                    common_keywords = list(filter(lambda x: x["value"] == keyword, keywords))
                    if common_keywords:
                        for k in common_keywords:
                            media.weight += k["weight"]
                    #media.weight += keywords.count(keyword)
                for credit in media.credits:
                    # Add weight based on the watchlist actors
                    if credit["job_id"] == "96":
                        common_actors = list(filter(lambda x: x["value"] == credit["person_id"], actors))
                        if common_actors:
                            for a in common_actors:
                                media.weight += a["weight"]
                        #media.weight += actors.count(credit["person_id"])
                    # Add weight based on the watchlist directors (more important)
                    elif credit["job_id"] == "537":
                        common_directors = list(filter(lambda x: x["value"] == credit["person_id"], directors))
                        if common_directors:
                            for d in common_directors:
                                media.weight += d["weight"] * 2
                        #media.weight += directors.count(credit["person_id"]) * 2
                if media.id in history_media_ids:
                    media.weight = 0

        # Sorting media by descending popularity and weight
        genre_medias = sorted(genre_medias, key=lambda x: x.popularity, reverse=True)
        genre_medias = sorted(genre_medias, key=lambda x: x.weight, reverse=True)

        return genre_medias[:10]