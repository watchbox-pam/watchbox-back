from typing import Dict, List, Set

from sqlalchemy import Float, Integer, and_, case, cast, distinct, extract, func, literal, or_, select, union_all
from sqlalchemy.dialects.postgresql import array

from database.db import SessionLocal
from database.models import (
    Movie as DBMovie,
    Playlist as DBPlaylist,
    User as DBUser,
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

ACTOR_CREDIT_TYPE = 1
CREW_CREDIT_TYPE = 2
DIRECTOR_JOB_ID = 537
TOP_BILLED_ORDER = 10

# Acteurs principaux (order < 10) + réalisateurs : les seuls crédits utilisés par le scoring.
_SCORED_CREDITS = or_(
    and_(t_credit.c.type == ACTOR_CREDIT_TYPE, t_credit.c.order < TOP_BILLED_ORDER),
    and_(t_credit.c.type == CREW_CREDIT_TYPE, t_credit.c.job_id == DIRECTOR_JOB_ID),
)
# array_agg de paires [person_id, job_id] dédoublonnées → tableau 2D d'entiers
_CREDIT_PAIRS = func.array_agg(distinct(array([t_credit.c.person_id, t_credit.c.job_id])))


def _to_credits(pairs) -> List[dict]:
    return [{"person_id": int(person_id), "job_id": int(job_id) if job_id is not None else None}
            for person_id, job_id in pairs]


class RecommendationRepository(IRecommendationRepository):
    def find_by_ids_recommendation(self, ids: List[int]):
        medias = []
        try:
            with SessionLocal() as session:
                results = session.execute(
                    select(
                        DBMovie.id,
                        func.array_agg(distinct(t_movie_movie_genre.c.genre_id)),
                        func.array_agg(distinct(t_media_keyword.c.keyword_id)),
                        _CREDIT_PAIRS,
                    )
                    .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == DBMovie.id)
                    .join(t_media_keyword, t_media_keyword.c.movie_id == DBMovie.id)
                    .join(t_credit, t_credit.c.movie_id == DBMovie.id)
                    .where(DBMovie.id.in_(ids), _SCORED_CREDITS)
                    .group_by(DBMovie.id)
                ).all()
                for movie_id, genres, keywords, credits in results:
                    medias.append(MovieRecommendation(
                        id=movie_id,
                        genres=genres,
                        keywords=keywords,
                        credits=_to_credits(credits),
                        poster_path="",
                        popularity=0,
                        title="",
                        weight=0
                    ))
        except Exception as e:
            print(e)
        return medias

    def find_candidates(self, movie_ids: List[int], include_adult: bool = False) -> List[MovieRecommendation]:
        medias: List[MovieRecommendation] = []
        try:
            with SessionLocal() as session:
                query = (
                    select(
                        DBMovie.id,
                        DBMovie.popularity,
                        DBMovie.title,
                        DBMovie.poster_path,
                        func.array_agg(distinct(t_movie_movie_genre.c.genre_id)),
                        func.array_agg(distinct(t_media_keyword.c.keyword_id)),
                        _CREDIT_PAIRS,
                        cast(extract("year", DBMovie.release_date), Integer),
                    )
                    .join(t_movie_movie_genre, t_movie_movie_genre.c.movie_id == DBMovie.id)
                    .join(t_media_keyword, t_media_keyword.c.movie_id == DBMovie.id)
                    .join(t_credit, t_credit.c.movie_id == DBMovie.id)
                    .where(DBMovie.id.in_(movie_ids), _SCORED_CREDITS)
                    .group_by(DBMovie.id)
                )
                if not include_adult:
                    query = query.where((DBMovie.adult == False) | (DBMovie.adult == None))  # noqa: E711, E712
                for movie_id, popularity, title, poster_path, genres, keywords, credits, release_year in session.execute(query).all():
                    medias.append(MovieRecommendation(
                        id=movie_id,
                        popularity=popularity,
                        title=title,
                        poster_path=poster_path,
                        genres=genres,
                        keywords=keywords,
                        credits=_to_credits(credits),
                        weight=0,
                        release_year=release_year
                    ))
        except Exception as e:
            print(e)
        return medias

    def get_movie_genres(self) -> Dict[int, Set[int]]:
        try:
            with SessionLocal() as session:
                results = session.execute(
                    select(t_movie_movie_genre.c.movie_id, func.array_agg(t_movie_movie_genre.c.genre_id))
                    .group_by(t_movie_movie_genre.c.movie_id)
                ).all()
                return {movie_id: set(genres) for movie_id, genres in results}
        except Exception as e:
            print(e)
            return {}

    def find_with_review(self, user_id: str, movie_ids: List[int]) -> List[MovieReview]:
        medias: List[MovieReview] = []
        try:
            with SessionLocal() as session:
                results = session.execute(
                    select(t_review.c.movie_id, t_review.c.rating)
                    .where(t_review.c.user_id == user_id, t_review.c.movie_id.in_(movie_ids))
                ).all()
                for movie_id, rating in results:
                    medias.append(MovieReview(
                        user_id=user_id,
                        movie_id=movie_id,
                        rating=rating
                    ))
        except Exception as e:
            print(e)
        return medias

    def get_all_reviews(self) -> List[dict]:
        try:
            with SessionLocal() as session:
                results = session.execute(
                    select(t_review.c.user_id, t_review.c.movie_id, t_review.c.rating)
                    .where(t_review.c.rating != None)  # noqa: E711
                ).all()
                return [{"user_id": user_id, "movie_id": movie_id, "rating": rating} for user_id, movie_id, rating in results]
        except Exception as e:
            print(e)
            return []

    def get_swipe_movie_ids(self, user_id: str) -> List[int]:
        try:
            with SessionLocal() as session:
                return list(session.execute(
                    select(t_swipe.c.movie_id).where(
                        t_swipe.c.user_id == user_id,
                        t_swipe.c.direction.in_(["like", "dislike"]),
                        t_swipe.c.movie_id != None,  # noqa: E711
                    )
                ).scalars())
        except Exception as e:
            print(e)
            return []

    def get_all_implicit_feedback(self) -> List[dict]:
        # Alimente l'ALS uniquement. Deux pièges à conserver :
        # - playlist_media n'a pas de user_id → on prend p.user_id (propriétaire de la playlist)
        # - les poids sont castés en float, sinon psycopg renvoie des Decimal et _train_als plante
        try:
            with SessionLocal() as session:
                playlist_feedback = (
                    select(
                        DBPlaylist.user_id,
                        t_playlist_media.c.movie_id,
                        cast(case((DBPlaylist.title == "Favoris", literal(2.0)), else_=literal(1.0)), Float).label("weight"),
                    )
                    .join(DBPlaylist, DBPlaylist.id == t_playlist_media.c.playlist_id)
                    .where(DBPlaylist.title.in_(["Watchlist", "Favoris"]))
                )
                swipe_feedback = (
                    select(
                        t_swipe.c.user_id,
                        t_swipe.c.movie_id,
                        cast(case((t_swipe.c.direction == "like", literal(1.5)), else_=literal(-0.5)), Float).label("weight"),
                    )
                    .where(t_swipe.c.direction.in_(["like", "dislike"]), t_swipe.c.movie_id != None)  # noqa: E711
                )
                results = session.execute(union_all(playlist_feedback, swipe_feedback)).all()
                return [{"user_id": user_id, "movie_id": movie_id, "weight": weight} for user_id, movie_id, weight in results]
        except Exception as e:
            print(e)
            return []

    def get_skip_movie_ids(self, user_id: str) -> List[int]:
        try:
            with SessionLocal() as session:
                return list(session.execute(
                    select(t_swipe.c.movie_id).where(
                        t_swipe.c.user_id == user_id,
                        t_swipe.c.direction == "skip",
                        t_swipe.c.movie_id != None,  # noqa: E711
                    )
                ).scalars())
        except Exception as e:
            print(e)
            return []

    def get_user_birth_year(self, user_id: str) -> int | None:
        try:
            with SessionLocal() as session:
                return session.execute(
                    select(cast(extract("year", DBUser.birthdate), Integer)).where(DBUser.id == user_id)
                ).scalar_one_or_none()
        except Exception as e:
            print(e)
            return None
