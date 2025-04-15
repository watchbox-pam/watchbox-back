from typing import List
import itertools
from domain.interfaces.i_recommendation_repository import IRecommendationRepository
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING
from utils.tmdb_service import call_tmdb_api


class RecommendationRepository(IRecommendationRepository):
    def get_by_emotion(self, emotion: Emotion, limit: int = 10) -> List[MovieListItem]:
        genre_ids = EMOTION_GENRE_MAPPING[emotion]
        movies = []

        for num_genres in range(len(genre_ids), 0, -1):
            for genres_subset in itertools.combinations(genre_ids, num_genres):
                genre_param = ",".join(map(str, genres_subset))
                endpoint = f"/discover/movie?with_genres={genre_param}&language=fr-FR&sort_by=popularity.desc"
                result = call_tmdb_api(endpoint)

                if "results" in result and result["results"]:
                    for movie_data in result["results"]:
                        if len(movies) >= limit:
                            return movies

                        movie = MovieListItem(
                            id=movie_data["id"],
                            title=movie_data.get("title", ""),
                            poster_path=movie_data.get("poster_path", "")
                        )

                        if not any(m.id == movie.id for m in movies):
                            movies.append(movie)

            if len(movies) >= limit:
                return movies

        return movies[:limit]