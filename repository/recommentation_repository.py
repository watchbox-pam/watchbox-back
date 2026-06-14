from typing import List

from sqlalchemy import and_, case, distinct, func, literal, or_, select

from database.db import SessionLocal
from database.models import (
    Movie,
    Playlist,
    t_credit,
    t_media_keyword,
    t_movie_movie_genre,
    t_playlist_media,
    t_review,
    t_swipe,
)
from domain.interfaces.repositories.i_recommendation_repository import IRecommendationRepository
from domain.models.movieRecommendation import MovieRecommendation
from domain.models.movieReview import MovieReview

# credit.type 1 = cast (top-billed, order < 10), 2 = crew (directors only, job_id 537)
_CREDIT_FILTER = or_(
    and_(t_credit.c.type == 1, t_credit.c.order < 10),
    and_(t_credit.c.type == 2, t_credit.c.job_id == 537),
)


class RecommendationRepository(IRecommendationRepository):
    def find_by_ids_recommendation(self, ids: List[int]):
        medias = []
        try:
            with SessionLocal() as session:
                stmt = (
                    select(
                        Movie.id,
                        func.array_agg(distinct(t_movie_movie_genre.c.genre_id)).label("genre_ids"),
                        func.array_agg(distinct(t_media_keyword.c.keyword_id)).label("keyword_ids"),
                        func.array_agg(distinct(func.row(t_credit.c.person_id, t_credit.c.job_id))).label("credit_ids"),
                    )
                    .select_from(
                        Movie.__table__
                        .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == Movie.id)
                        .join(t_media_keyword, t_media_keyword.c.movie_id == Movie.id)
                        .join(t_credit, t_credit.c.movie_id == Movie.id)
                    )
                    .where(Movie.id.in_(ids), _CREDIT_FILTER)
                    .group_by(Movie.id)
                )
                for result in session.execute(stmt):
                    credit_list = [{"person_id": c[0], "job_id": c[1]} for c in result[3]]
                    medias.append(MovieRecommendation(
                        id=result[0],
                        genres=result[1],
                        keywords=result[2],
                        credits=credit_list,
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
            with SessionLocal() as session:
                stmt = (
                    select(
                        t_movie_movie_genre.c.movie_id.label("id"),
                        func.max(Movie.popularity).label("popularity"),
                        Movie.title.label("title"),
                        func.max(Movie.poster_path).label("poster_path"),
                        func.array_agg(distinct(t_movie_movie_genre.c.genre_id)).label("genre_ids"),
                        func.array_agg(distinct(t_media_keyword.c.keyword_id)).label("keyword_ids"),
                        func.array_agg(distinct(func.row(t_credit.c.person_id, t_credit.c.job_id))).label("credit_ids"),
                    )
                    .select_from(
                        t_movie_movie_genre
                        .join(Movie.__table__, Movie.id == t_movie_movie_genre.c.movie_id)
                        .join(t_media_keyword, t_media_keyword.c.movie_id == Movie.id)
                        .join(t_credit, t_credit.c.movie_id == Movie.id)
                    )
                    .where(
                        t_movie_movie_genre.c.genre_id.in_(genres),
                        _CREDIT_FILTER,
                        or_(literal(include_adult), Movie.adult.isnot(True)),
                    )
                    .group_by(t_movie_movie_genre.c.movie_id, Movie.title)
                )
                for result in session.execute(stmt):
                    credit_list = [{"person_id": c[0], "job_id": c[1]} for c in result[6]]
                    medias.append(MovieRecommendation(
                        id=result[0],
                        popularity=result[1],
                        title=result[2],
                        poster_path=result[3],
                        genres=result[4],
                        keywords=result[5],
                        credits=credit_list,
                        weight=0
                    ))
        except Exception as e:
            print(e)
        return medias

    def find_with_review(self, user_id: str, movie_ids: List[int]) -> List[MovieReview]:
        medias: List[MovieReview] = []
        try:
            with SessionLocal() as session:
                stmt = (
                    select(t_review.c.movie_id, t_review.c.rating)
                    .where(
                        t_review.c.user_id == user_id,
                        t_review.c.movie_id.in_(movie_ids),
                    )
                )
                for result in session.execute(stmt):
                    medias.append(MovieReview(
                        user_id=user_id,
                        movie_id=result[0],
                        rating=result[1]
                    ))
        except Exception as e:
            print(e)
        return medias

    def get_all_reviews(self) -> List[dict]:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(t_review.c.user_id, t_review.c.movie_id, t_review.c.rating)
                    .where(t_review.c.rating.isnot(None))
                )
                return [
                    {"user_id": r[0], "movie_id": r[1], "rating": r[2]}
                    for r in session.execute(stmt)
                ]
        except Exception as e:
            print(e)
            return []

    def get_swipe_movie_ids(self, user_id: str) -> List[int]:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(t_swipe.c.movie_id)
                    .where(
                        t_swipe.c.user_id == user_id,
                        t_swipe.c.direction.in_(["like", "dislike"]),
                        t_swipe.c.movie_id.isnot(None),
                    )
                )
                return [row[0] for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []

    def get_all_implicit_feedback(self) -> List[dict]:
        try:
            with SessionLocal() as session:
                playlist_part = (
                    select(
                        Playlist.user_id,
                        t_playlist_media.c.movie_id,
                        case((Playlist.title == "Favoris", 2.0), else_=1.0).label("weight"),
                    )
                    .select_from(
                        t_playlist_media.join(Playlist, Playlist.id == t_playlist_media.c.playlist_id)
                    )
                    .where(Playlist.title.in_(["Watchlist", "Favoris"]))
                )
                swipe_part = (
                    select(
                        t_swipe.c.user_id,
                        t_swipe.c.movie_id,
                        case((t_swipe.c.direction == "like", 1.5), else_=-0.5).label("weight"),
                    )
                    .where(
                        t_swipe.c.direction.in_(["like", "dislike"]),
                        t_swipe.c.movie_id.isnot(None),
                    )
                )
                stmt = playlist_part.union_all(swipe_part)
                return [
                    {"user_id": r[0], "movie_id": r[1], "weight": r[2]}
                    for r in session.execute(stmt)
                ]
        except Exception as e:
            print(e)
            return []

    def get_skip_movie_ids(self, user_id: str) -> List[int]:
        try:
            with SessionLocal() as session:
                stmt = (
                    select(t_swipe.c.movie_id)
                    .where(
                        t_swipe.c.user_id == user_id,
                        t_swipe.c.direction == "skip",
                        t_swipe.c.movie_id.isnot(None),
                    )
                )
                return [row[0] for row in session.execute(stmt)]
        except Exception as e:
            print(e)
            return []
