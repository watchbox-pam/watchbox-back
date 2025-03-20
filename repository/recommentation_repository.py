from typing import List
import random
from domain.interfaces.i_recommendation_repository import IRecommendationRepository
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING
from utils.tmdb_service import call_tmdb_api


class RecommendationRepository(IRecommendationRepository):
    def get_by_emotion(self, emotion: Emotion, limit: int = 10) -> List[MovieListItem]:
        genre_ids = EMOTION_GENRE_MAPPING[emotion]

        # Choose a random genre from those associated with the emotion
        genre_id = random.choice(genre_ids)

        # Get movies by genre
        endpoint = f"/discover/movie?with_genres={genre_id}&language=fr-FR&sort_by=popularity.desc"
        result = call_tmdb_api(endpoint)

        movies = []
        if "results" in result:
            for movie_data in result["results"][:limit]:
                movie = MovieListItem(
                    id=movie_data["id"],
                    title=movie_data.get("title", ""),
                    poster_path=movie_data.get("poster_path", "")
                )
                movies.append(movie)

        return movies