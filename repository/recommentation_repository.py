from typing import List, Dict, Any
import itertools
from domain.interfaces.i_recommendation_repository import IRecommendationRepository
from domain.models.movie_list_item import MovieListItem
from domain.models.emotion import Emotion, EMOTION_GENRE_MAPPING
from utils.tmdb_service import call_tmdb_api


class RecommendationRepository(IRecommendationRepository):
    def get_by_emotion(self, emotion: Emotion, limit: int = 10) -> List[MovieListItem]:
        genre_ids = EMOTION_GENRE_MAPPING[emotion]
        scored_movies: Dict[int, Dict[str, Any]] = {}

        for num_genres in range(len(genre_ids), 0, -1):
            for genres_subset in itertools.combinations(genre_ids, num_genres):
                genre_param = ",".join(map(str, genres_subset))
                endpoint = f"/discover/movie?with_genres={genre_param}&language=fr-FR&sort_by=popularity.desc"
                result = call_tmdb_api(endpoint)

                if "results" in result and result["results"]:
                    match_weight = num_genres / len(genre_ids)

                    for idx, movie_data in enumerate(result["results"]):
                        movie_id = movie_data["id"]

                        popularity_weight = 1 - (idx / len(result["results"]))
                        vote_weight = movie_data.get("vote_average", 5) / 10

                        score = (match_weight * 0.5) + (popularity_weight * 0.3) + (vote_weight * 0.2)

                        if movie_id not in scored_movies or score > scored_movies[movie_id]["score"]:
                            scored_movies[movie_id] = {
                                "data": movie_data,
                                "score": score
                            }

            if len(scored_movies) >= limit * 3:
                break

        final_movies = []
        sorted_movies = sorted(scored_movies.values(), key=lambda x: x["score"], reverse=True)

        for movie in sorted_movies:
            if not self._is_too_similar(movie["data"], [m["data"] for m in final_movies]):
                final_movies.append(movie)
                if len(final_movies) >= limit:
                    break

        if len(final_movies) < limit:
            remaining_movies = [m for m in sorted_movies if m not in final_movies]
            final_movies.extend(remaining_movies[:limit - len(final_movies)])

        return [
            MovieListItem(
                id=movie["data"]["id"],
                title=movie["data"].get("title", ""),
                poster_path=movie["data"].get("poster_path", "")
            ) for movie in final_movies[:limit]
        ]

    def _is_too_similar(self, movie: Dict[str, Any], selected_movies: List[Dict[str, Any]]) -> bool:
        """
        Détermine si un film est trop similaire aux films déjà sélectionnés.
        Un film est considéré comme trop similaire s'il partage trop de genres
        avec un film déjà sélectionné.
        """
        if not selected_movies:
            return False

        movie_genres = set(movie.get("genre_ids", []))

        for selected_movie in selected_movies:
            selected_genres = set(selected_movie.get("genre_ids", []))

            if movie_genres and selected_genres:
                common_genres = movie_genres.intersection(selected_genres)
                similarity = len(common_genres) / max(len(movie_genres), len(selected_genres))

                if similarity > 0.75:
                    return True

        return False