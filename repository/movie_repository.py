from typing import Optional, List

import db_config
from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import Movie, PopularMovieList, MovieDetail
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movie_list_item import MovieListItem
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
            print(f"[DEBUG] Calcul du runtime pour les IDs : {movie_ids}")
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT SUM(runtime) FROM public.movie WHERE id = ANY(%s);", (movie_ids,))
                    result = cur.fetchone()
                    print(f"[DEBUG] Résultat SQL : {result}")
                    return result[0] if result and result[0] else 0
        except Exception as e:
            print(f"[ERREUR] Exception dans movie_runtime : {e}")
            return 0
        
    def get_random_movies(self, count: int = 50) -> Optional[List[MovieListItem]]:

        movies: List[Movie] = []

        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT id, title, poster_path FROM public.movie 
                        WHERE popularity >= 70
                        ORDER BY RANDOM() 
                        LIMIT %s;
                    """
                    cur.execute(query, (count,))
                    results = cur.fetchall()

                    for result in results:
                        movies.append(MovieListItem(
                            id=result[0],
                            title=result[1],
                            poster_path=result[2]
                        ))

        except Exception as e:
            print(e)

        return movies