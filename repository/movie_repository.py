from typing import Optional

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import Movie, PopularMovieList
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
    
    def find_by_time_window(self, time_window: str, page: int) -> Optional[PopularMovieList]:
        endpoint = f"/trending/movie/{time_window}?page={page}"

        result = call_tmdb_api(endpoint)

        print(result)

        movies = PopularMovieList(
            page=result["page"],
            results=result["results"],
            total_results=result["total_pages"],
            total_pages=result["total_results"]
        )

        return movies