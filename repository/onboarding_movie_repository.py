from typing import Any, Dict, List

from sqlalchemy import exists, false, func, select

from database.db import SessionLocal
from database.models import Movie as DBMovie
from database.models import Playlist as DBPlaylist
from database.models import t_media_media_provider, t_movie_movie_genre, t_playlist_media, t_review, t_swipe
from domain.interfaces.repositories.i_onboarding_movie_repository import IOnboardingMovieRepository


class OnboardingMovieRepository(IOnboardingMovieRepository):
    COUNTRY = "FR"

    def get_candidates(self, user_id: str, include_adult: bool, provider_ids: List[int], pool_size: int) -> List[Dict[str, Any]]:
        genre_ids = (
            select(func.array_agg(t_movie_movie_genre.c.genre_id))
            .where(t_movie_movie_genre.c.movie_id == DBMovie.id)
            .correlate(DBMovie)
            .scalar_subquery()
        )

        if provider_ids:
            available = exists().where(
                t_media_media_provider.c.movie_id == DBMovie.id,
                t_media_media_provider.c.country == self.COUNTRY,
                t_media_media_provider.c.media_provider_id.in_(provider_ids),
            )
        else:
            available = false()

        query = (
            select(
                DBMovie.id,
                DBMovie.title,
                DBMovie.poster_path,
                DBMovie.popularity,
                genre_ids.label("genre_ids"),
                available.label("available"),
            )
            .where(
                DBMovie.poster_path.is_not(None),
                DBMovie.title.is_not(None),
                # Mêmes exclusions que /movies/random : déjà swipé, noté ou en playlist
                ~exists().where(t_swipe.c.user_id == user_id, t_swipe.c.movie_id == DBMovie.id),
                ~exists().where(t_review.c.user_id == user_id, t_review.c.movie_id == DBMovie.id),
                ~exists().where(
                    t_playlist_media.c.playlist_id == DBPlaylist.id,
                    DBPlaylist.user_id == user_id,
                    t_playlist_media.c.movie_id == DBMovie.id,
                ),
            )
            .order_by(available.desc(), DBMovie.popularity.desc().nulls_last())
            .limit(pool_size)
        )
        if not include_adult:
            query = query.where((DBMovie.adult == False) | (DBMovie.adult == None))  # noqa: E711,E712

        with SessionLocal() as session:
            rows = session.execute(query).all()

        return [
            {
                "id": row.id,
                "title": row.title,
                "poster_path": row.poster_path,
                "popularity": row.popularity,
                "genre_ids": list(row.genre_ids or []),
                "available": bool(row.available),
            }
            for row in rows
        ]
