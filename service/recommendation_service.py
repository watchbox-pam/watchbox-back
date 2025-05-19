from typing import List

from domain.interfaces.repositories.i_playlist_repository import IPlaylistRepository
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING


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

        watchlist_media_ids = []
        for media in user_watchlist:
            watchlist_media_ids.append(media.movie_id)

        history_media_ids = []
        for media in user_history:
            history_media_ids.append(media.movie_id)

        favorites_media_ids = []
        for media in user_favorites:
            favorites_media_ids.append(media.movie_id)

        # Fetching infos of playlists
        watchlist_media_infos: List[MovieRecommendation] = self.repository.find_by_ids_recommendation(watchlist_media_ids)
        history_media_infos: List[MovieRecommendation] = self.repository.find_by_ids_recommendation(history_media_ids)
        favorites_media_infos: List[MovieRecommendation] = self.repository.find_by_ids_recommendation(favorites_media_ids)

        watchlist_movie_ids = []
        history_movie_ids = []
        favorites_movie_ids = []
        keywords = []
        actors = []
        directors = []

        # Adding data from the watchlist medias
        for watchlist_media in watchlist_media_infos:
            watchlist_movie_ids.append(watchlist_media.id)
            for keyword in watchlist_media.keywords:
                keywords.append(keyword)
            for credit in watchlist_media.credits:
                if credit["job_id"] == "96":
                    actors.append(credit["person_id"])
                elif credit["job_id"] == "537":
                    directors.append(credit["person_id"])

        # Getting medias matching selected emotion / genres
        genre_medias = self.repository.find_by_genres(EMOTION_GENRE_MAPPING[emotion])

        for media in genre_medias:
            media.weight = len(media.genres)
            if len(user_watchlist) > 0:
                # Check if media is in the user watchlist
                if media.id in watchlist_movie_ids:
                    media.weight += 10
                # Add weight based on the watchlist keywords
                for keyword in media.keywords:
                    media.weight += keywords.count(keyword)
                for credit in media.credits:
                    # Add weight based on the watchlist actors
                    if credit["job_id"] == "96":
                        media.weight += actors.count(credit["person_id"])
                    # Add weight based on the watchlist directors (more important)
                    elif credit["job_id"] == "537":
                        media.weight += directors.count(credit["person_id"]) * 2

        # Sorting media by descending popularity and weight
        genre_medias = sorted(genre_medias, key=lambda x: x.popularity, reverse=True)
        genre_medias = sorted(genre_medias, key=lambda x: x.weight, reverse=True)

        return genre_medias[:10]