from typing import List

import db_config
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movieReview import MovieReview


class RecommendationRepository(IRecommendationRepository):
    def find_by_ids_recommendation(self, ids: List[int]):
        medias = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = ("SELECT "
                             "DISTINCT(m.id), "
                             "array_agg(DISTINCT mg.genre_id) AS genre_ids, "
                             "array_agg(DISTINCT mk.keyword_id) AS keyword_ids, "
                             "array_agg(DISTINCT (c.person_id, c.job_id)) AS credit_ids "
                             "FROM public.movie m "
                             "INNER JOIN public.movie_movie_genre mg ON mg.movie_id = m.id "
                             "INNER JOIN public.media_keyword mk ON mk.movie_id = m.id "
                             "INNER JOIN public.credit c ON c.movie_id = m.id "
                             "WHERE m.id = ANY(%s) "
                             "AND ((c.type = 1 AND c.order < 10) OR (c.type = 2 AND c.job_id = 537))"
                             "GROUP BY m.id;")

                    cur.execute(query, (ids,))
                    results = cur.fetchall()

                    if results is not None:
                        for result in results:
                            credits = []
                            for credit in result[3]:
                                credits.append({"person_id": credit[0], "job_id": credit[1]})
                            medias.append(MovieRecommendation(
                                id=result[0],
                                genres=result[1],
                                keywords=result[2],
                                credits=credits,
                                poster_path="",
                                popularity=0,
                                title="",
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
                             "mg.movie_id as id, MAX(m.popularity) as popularity, m.title as title, MAX(m.poster_path) as poster_path, "
                             "array_agg(DISTINCT mg.genre_id) AS genre_ids, "
                             "array_agg(DISTINCT mk.keyword_id) AS keyword_ids, "
                             "array_agg(DISTINCT (c.person_id, c.job_id)) AS credit_ids "
                             "FROM public.movie_movie_genre mg "
                             "INNER JOIN public.movie m on m.id = mg.movie_id "
                             "INNER JOIN public.media_keyword mk ON mk.movie_id = m.id "
                             "INNER JOIN public.credit c ON c.movie_id = m.id "
                             "WHERE mg.genre_id = ANY(%s) "
                             "AND ((c.type = 1 AND c.order < 10) OR (c.type = 2 AND c.job_id = 537))"
                             "group by mg.movie_id, m.title;")

                    cur.execute(query, (genres,))
                    results = cur.fetchall()

                    if results is not None:
                        for result in results:
                            credits = []
                            for credit in result[6]:
                                credits.append({"person_id": credit[0], "job_id": credit[1]})
                            medias.append(MovieRecommendation(
                                id=result[0],
                                popularity=result[1],
                                title=result[2],
                                poster_path=result[3],
                                genres=result[4],
                                keywords=result[5],
                                credits=credits,
                                weight=0
                            ))

        except Exception as e:
            print(e)

        return medias

    def find_with_review(self, user_id: str, movie_ids: List[int]) -> List[MovieReview]:
        medias: List[MovieReview] = []
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    query = "SELECT movie_id, rating FROM public.review WHERE user_id = %s AND movie_id = ANY(%s)"

                    cur.execute(query, (user_id, movie_ids))
                    results = cur.fetchall()

                    if results is not None:
                        for result in results:
                            medias.append(MovieReview(
                                user_id=user_id,
                                movie_id=result[0],
                                rating=result[1]
                            ))

        except Exception as e:
            print(e)

        return medias