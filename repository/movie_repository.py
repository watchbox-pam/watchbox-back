from typing import Optional, List

import db_config
from domain.interfaces.repositories.i_movie_repository import IMovieRepository
from domain.models.movie import Movie, PopularMovieList, MovieDetail
from domain.models.movieRecommendation import MovieRecommendation
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

        movies = PopularMovieList(
            page=result["page"],
            results=result["results"],
            total_results=result["total_pages"],
            total_pages=result["total_results"]
        )

        return movies

    def find_by_ids_recommendation(self, ids: List[int]):
        medias = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = ("SELECT "
                    "DISTINCT(m.id), "
                    "array_agg(DISTINCT mg.genre_id) AS genre_ids, "
                    "array_agg(DISTINCT mk.keyword_id) AS keyword_ids "
                    "FROM public.movie m "
                    "INNER JOIN public.movie_movie_genre mg ON mg.movie_id = m.id "
                    "INNER JOIN public.media_keyword mk ON mk.movie_id = m.id "
                    "WHERE m.id = ANY(%s) "
                    "GROUP BY m.id;")

                    cur.execute(query, (ids,))
                    results = cur.fetchall()

                    if results is not None:
                        for result in results:
                            medias.append(MovieRecommendation(
                                id=result[0],
                                genres=result[1],
                                keywords=result[2],
                                cast=[],
                                crew=[],
                                weight=0
                            ))

        except Exception as e:
            print(e)

        return medias


    def find_by_genres(self, genres: List[int]) -> List[MovieRecommendation]:
        medias: List[MovieRecommendation] = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = ("SELECT "
                             "movie_id as id, MAX(m.popularity) as popularity, m.title as title, MAX(m.poster_path) as poster_path, "
                             "array_agg(DISTINCT mg.genre_id) AS genre_ids "
                             "FROM public.movie_movie_genre mg "
                             "INNER JOIN public.movie m on m.id = mg.movie_id "
                             "WHERE mg.genre_id = ANY(%s)"
                             "group by mg.movie_id, m.title;")

                    cur.execute(query, (genres,))
                    results = cur.fetchall()

                    if results is not None:
                        for result in results:
                            medias.append(MovieRecommendation(
                                id=result[0],
                                popularity=result[1],
                                title=result[2],
                                poster_path=result[3],
                                genres=result[4],
                                keywords=[],
                                cast=[],
                                crew=[],
                                weight=0
                            ))

        except Exception as e:
            print(e)

        return medias