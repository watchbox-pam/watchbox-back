from typing import Optional

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import Movie
from utils.tmdb_service import call_tmdb_api


class MovieRepository(IMovieRepository):
    def find_by_id(self, movie_id: int) -> Optional[Movie]:
        endpoint = f"/movie/{movie_id}?language=fr-FR"

        result = call_tmdb_api(endpoint)

        movie = Movie(
            id=result["id"],
            adult=result["adult"],
            backdrop_path=result["backdrop_path"],
            budget=result["budget"],
            original_language=result["original_language"],
            original_title=result["original_title"],
            overview=result["overview"],
            poster_path=result["poster_path"],
            release_date=result["release_date"],
            revenue=result["revenue"],
            runtime=result["runtime"],
            status=result["status"],
            title=result["title"],
            video=result["video"],
            infos_complete=True
        )

        return movie


    def search(self, search_term: str) -> Optional[list[Movie]]:
        endpoint = f"/search/movie?query={search_term}&include_adult=false&language=fr-FR"

        result = call_tmdb_api(endpoint)

        movies: list[Movie] = []

        for res in result["results"]:
            movies.append(Movie(
                id=res["id"],
                adult=res["adult"],
                backdrop_path=res["backdrop_path"],
                budget=0,
                original_language=res["original_language"],
                original_title=res["original_title"],
                overview=res["overview"],
                poster_path=res["poster_path"],
                release_date=res["release_date"],
                revenue=0,
                runtime=0,
                status="",
                title=res["title"],
                video=res["video"],
                infos_complete=True
            ))

        return movies