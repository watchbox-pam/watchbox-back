from typing import Optional, List

from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import PopularMovieList, MovieDetail
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movie_list_item import MovieListItem
from utils.tmdb_service import call_tmdb_api
from database.db import SessionLocal
from database.models import Movie as DBMovie
from sqlalchemy import func

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


    def search(self, search_term: str) -> Optional[list[MovieDetail]]:
        endpoint = f"/search/movie?query={search_term}&include_adult=false&language=fr-FR"

        result = call_tmdb_api(endpoint)

        movies: list[MovieDetail] = []

        for res in result["results"]:
            movies.append(MovieDetail(
                id=res["id"],
                adult=res["adult"],
                backdrop_path=res["backdrop_path"],
                budget=0,
                genres=[],
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
        endpoint = f"/trending/movie/{time_window}?page={page}&language=fr-FR"

        result = call_tmdb_api(endpoint)

        movies = PopularMovieList(
            page=result["page"],
            results=result["results"],
            total_results=result["total_pages"],
            total_pages=result["total_results"]
        )

        return movies

    def find_by_genre(self, genre: str) -> Optional[PopularMovieList]:
        endpoint = f"/discover/movie?with_genres={genre}&include_adult=false&include_video=false&language=fr-FR&page=1&sort_by=popularity.desc"

        result = call_tmdb_api(endpoint)

        movies = PopularMovieList(
            page=result["page"],
            results=result["results"],
            total_results=result["total_pages"],
            total_pages=result["total_results"]
        )

        return movies

    def movie_runtime(self, movie_ids: List[int]) -> int:
        try:
            with SessionLocal() as session:
                movies = session.query(DBMovie).filter(DBMovie.id.in_(movie_ids))
                total_runtime = sum(movie.runtime for movie in movies)
                return total_runtime
        except Exception as e:
            print(f"[ERREUR] Exception dans movie_runtime : {e}")
            return 0
        
    def get_random_movies(self, count: int = 50, include_adult: bool = False) -> Optional[List[MovieListItem]]:

        movies: List[DBMovie] = []

        try:
            with SessionLocal() as session:
                query = session.query(DBMovie).filter(DBMovie.popularity >= 70)
                if not include_adult:
                    query = query.filter((DBMovie.adult == False) | (DBMovie.adult == None))
                results = query.order_by(func.random()).limit(count).all()
                for result in results:
                    movies.append(MovieListItem(
                        id=result.id,
                        title=result.title,
                        poster_path=result.poster_path
                    ))

        except Exception as e:
            print(e)

        return movies