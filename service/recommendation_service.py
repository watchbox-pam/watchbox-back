from typing import List

from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.interfaces.services.i_movie_service import IMovieService
from domain.interfaces.services.i_playlist_service import IPlaylistService
from domain.interfaces.services.i_recommendation_service import IRecommendationService
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING


class RecommendationService(IRecommendationService):
    def __init__(self, repository: IRecommendationRepository, playlistService: IPlaylistService,
                 movieService: IMovieService):
        self.repository = repository
        self.playlist_service = playlistService
        self.movie_service = movieService

    def get_by_emotion(self, emotion: Emotion, limit: int = 10) -> List[MovieListItem]:
        print(emotion)
        return self.repository.get_by_emotion(emotion, limit)


    def get_recommendations(self, emotion: Emotion, user_id: str):

        recommended_medias: List[MovieRecommendation] = []

        #Fetch medias corresponding to the genres
        genre_medias = self.movie_service.find_by_genres(EMOTION_GENRE_MAPPING[emotion])
        for media in genre_medias:
            media.weight = len(media.genres)

        print(genre_medias[0])

        genre_medias = sorted(genre_medias, key=lambda x: x.popularity, reverse=True)
        print(genre_medias[0])
        genre_medias = sorted(genre_medias, key=lambda x: x.weight, reverse=True)
        for i in range(0, 5):
            print(genre_medias[i])

        # Fetch user watchlist
        '''user_playlists = self.playlist_service.get_playlists_by_user_id(user_id)
        user_watchlist_id: str = ""
        for item in user_playlists:
            if item.title == 'Watchlist':
                user_watchlist_id = str(item.id)
                break
        user_watchlist = self.playlist_service.get_playlist_medias(user_watchlist_id)
        if len(user_watchlist) == 0:
            return []

        media_ids = []
        for media in user_watchlist:
            media_ids.append(media.movie_id)

        watchlist_media_infos = self.movie_service.find_by_ids_recommendation(media_ids)'''

        return genre_medias