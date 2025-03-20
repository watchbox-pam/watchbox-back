from typing import Optional

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import Movie, PopularMovieList, MovieDetail
from utils.tmdb_service import call_tmdb_api


class MovieRepository(IMovieRepository):
    def find_by_id(self, movie_id: int) -> Optional[MovieDetail]:
        endpoint = f"/movie/{movie_id}?language=fr-FR"

        result = call_tmdb_api(endpoint)

        movie = MovieDetail(
            id=result["id"],
            adult=result["adult"],
            backdrop_path=result["backdrop_path"],
            budget=result["budget"],
            genres=result["genres"],
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