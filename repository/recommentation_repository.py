from typing import List

import db_config
from database.db import SessionLocal
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movieReview import MovieReview
from database.models.movie import Movie as DBMovie
from database.models.movie_translation import MovieTranslation as DBMovieTranslation
from database.models.movie_genre import MovieGenre as DBMovieGenre
from database.models.keyword import Keyword as DBKeyword
from database.models.association_tables import t_credit, t_movie_movie_genre, t_media_keyword
from sqlalchemy import select, distinct, tuple_
from sqlalchemy.sql import func


class RecommendationRepository(IRecommendationRepository):
    def find_by_ids_recommendation(self, ids: List[int]):
        medias = []
        try:
            # with db_config.connect_to_db() as conn:
            #     with conn.cursor() as cur:
            #         query = ("SELECT "
            #                  "DISTINCT(m.id), "
            #                  "array_agg(DISTINCT mg.genre_id) AS genre_ids, "
            #                  "array_agg(DISTINCT mk.keyword_id) AS keyword_ids, "
            #                  "array_agg(DISTINCT (c.person_id, c.job_id)) AS credit_ids "
            #                  "FROM public.movie m "
            #                  "INNER JOIN public.movie_movie_genre mg ON mg.movie_id = m.id "
            #                  "INNER JOIN public.media_keyword mk ON mk.movie_id = m.id "
            #                  "INNER JOIN public.credit c ON c.movie_id = m.id "
            #                  "WHERE m.id = ANY(%s) "
            #                  "AND ((c.type = 1 AND c.order < 10) OR (c.type = 2 AND c.job_id = 537))"
            #                  "GROUP BY m.id;")

            #         cur.execute(query, (ids,))
            #         results = cur.fetchall()

                with SessionLocal() as session:
                    results = session.execute(
                        select(
                            DBMovie.id.distinct(),
                            func.array_agg(distinct(t_movie_movie_genre.c.genre_id)).label("genre_ids"),
                            func.array_agg(distinct(t_media_keyword.c.keyword_id)).label("keyword_ids"),
                            func.array_agg(distinct(tuple_(t_credit.c.person_id, t_credit.c.job_id))).label("credit_ids")
                        ).select_from(DBMovie).join(
                                    t_movie_movie_genre, DBMovie.id == t_movie_movie_genre.c.movie_id
                                ).join(
                                    t_media_keyword, DBMovie.id == t_media_keyword.c.movie_id
                                ).join(
                                    t_credit, DBMovie.id == t_credit.c.movie_id
                                ).where(
                            DBMovie.id.in_(ids), ((t_credit.c.type == 1) & (t_credit.c.order < 10)) | ((t_credit.c.type == 2) & (t_credit.c.job_id == 537))
                        ).group_by(DBMovie.id)
                    ).fetchall()
                    print(f"Results for IDs {ids}: {results}")

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

    def find_by_genres(self, genres: List[int], include_adult: bool = False) -> List[MovieRecommendation]:
        medias: List[MovieRecommendation] = []
        try:
            # with db_config.connect_to_db() as conn:
            #     with conn.cursor() as cur:
            #         query = ("SELECT "
            #                  "mg.movie_id as id, MAX(m.popularity) as popularity, m.title as title, MAX(m.poster_path) as poster_path, "
            #                  "array_agg(DISTINCT mg.genre_id) AS genre_ids, "
            #                  "array_agg(DISTINCT mk.keyword_id) AS keyword_ids, "
            #                  "array_agg(DISTINCT (c.person_id, c.job_id)) AS credit_ids "
            #                  "FROM public.movie_movie_genre mg "
            #                  "INNER JOIN public.movie m on m.id = mg.movie_id "
            #                  "INNER JOIN public.media_keyword mk ON mk.movie_id = m.id "
            #                  "INNER JOIN public.credit c ON c.movie_id = m.id "
            #                  "WHERE mg.genre_id = ANY(%s) "
            #                  "AND ((c.type = 1 AND c.order < 10) OR (c.type = 2 AND c.job_id = 537)) "
            #                  "AND (%s OR m.adult IS NOT TRUE) "
            #                  "group by mg.movie_id, m.title;")
            #         cur.execute(query, (genres, include_adult))
            #         results = cur.fetchall()

            translation_subquery = (
                select(
                    DBMovieTranslation.movie_id.label("movie_id"),
                    DBMovieTranslation.title.label("title"),
                    DBMovieTranslation.poster_path.label("poster_path"),
                )
                .where(DBMovieTranslation.language_iso == "fr")
                .subquery()
            ).outerjoin(DBMovie, DBMovie.id == DBMovieTranslation.movie_id)

            with SessionLocal() as session:
                results = session.execute(
                    select(
                        t_movie_movie_genre.c.movie_id.label("id"),
                        func.max(DBMovie.popularity).label("popularity"),
                        # DBMovie.title.label("title"),
                        # func.max(DBMovie.poster_path).label("poster_path"),
                        translation_subquery.c.title.label("title"),
                        translation_subquery.c.poster_path.label("poster_path"),
                        func.max(translation_subquery.c.poster_path).label("poster_path"),
                        func.array_agg(distinct(t_movie_movie_genre.c.genre_id)).label("genre_ids"),
                        func.array_agg(distinct(t_media_keyword.c.keyword_id)).label("keyword_ids"),
                        func.array_agg(distinct(tuple_(t_credit.c.person_id, t_credit.c.job_id))).label("credit_ids")
                    ).select_from(
                            t_movie_movie_genre.join(
                                DBMovie, DBMovie.id == t_movie_movie_genre.c.movie_id
                            ).join(
                                # to get the translation for the title and poster_path
                                translation_subquery, translation_subquery.c.movie_id == DBMovie.id
                            ).join(
                                t_media_keyword, DBMovie.id == t_media_keyword.c.movie_id
                            ).join(
                                t_credit, DBMovie.id == t_credit.c.movie_id
                            )
                    ).where(
                        t_movie_movie_genre.c.genre_id.in_(genres),
                        ((t_credit.c.type == 1) & (t_credit.c.order < 10)) | ((t_credit.c.type == 2) & (t_credit.c.job_id == 537)),
                        (include_adult | (DBMovie.adult.isnot(True)))
                    ).group_by(t_movie_movie_genre.c.movie_id, translation_subquery.c.title)
                ).fetchall()

                print(f"Results for genres {genres} (include_adult={include_adult}): {results}")

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

    def get_all_reviews(self) -> List[dict]:  # 👈 ajouté
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, movie_id, rating
                        FROM public.review
                        WHERE rating IS NOT NULL
                    """)
                    return [{"user_id": r[0], "movie_id": r[1], "rating": r[2]} for r in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_swipe_movie_ids(self, user_id: str) -> List[int]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT movie_id FROM public.swipe
                        WHERE user_id = %s
                          AND direction IN ('like', 'dislike')
                          AND movie_id IS NOT NULL
                    """, (user_id,))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_all_implicit_feedback(self) -> List[dict]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT pm.user_id, pm.movie_id,
                            CASE WHEN p.title = 'Favoris' THEN 2.0 ELSE 1.0 END as weight
                        FROM public.playlist_media pm
                        JOIN public.playlist p ON p.id = pm.playlist_id
                        WHERE p.title IN ('Watchlist', 'Favoris')
                        UNION ALL
                        SELECT user_id, movie_id,
                            CASE WHEN direction = 'like' THEN 1.5 ELSE -0.5 END as weight
                        FROM public.swipe
                        WHERE direction IN ('like', 'dislike')
                          AND movie_id IS NOT NULL
                    """)
                    return [{"user_id": r[0], "movie_id": r[1], "weight": r[2]} for r in cur.fetchall()]
        except Exception as e:
            print(e)
            return []

    def get_skip_movie_ids(self, user_id: str) -> List[int]:
        try:
            with db_config.connect_to_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT movie_id FROM public.swipe
                        WHERE user_id = %s
                          AND direction = 'skip'
                          AND movie_id IS NOT NULL
                    """, (user_id,))
                    return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(e)
            return []