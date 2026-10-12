from typing import Optional

from sqlalchemy import func

from database.db import SessionLocal
from database.models import Movie as DBMovie
from domain.interfaces.repositories.i_admin_movie_repository import IAdminMovieRepository


class AdminMovieRepository(IAdminMovieRepository):
    def count(self) -> int:
        with SessionLocal() as session:
            return session.query(func.count(DBMovie.id)).scalar() or 0

    def find_page(self, offset: int, limit: int) -> list[DBMovie]:
        with SessionLocal() as session:
            return (
                session.query(DBMovie)
                .order_by(DBMovie.title.asc().nullslast())
                .offset(offset)
                .limit(limit)
                .all()
            )

    def find_by_id(self, movie_id: int) -> Optional[DBMovie]:
        with SessionLocal() as session:
            return (
                session.query(DBMovie)
                .filter(DBMovie.id == movie_id)
                .first()
            )

    def create(self, data: dict) -> DBMovie:
        with SessionLocal() as session:
            movie = DBMovie(**data, genre=[])

            session.add(movie)
            session.commit()
            session.refresh(movie)

            return movie

    def update(self, movie_id: int, data: dict) -> Optional[DBMovie]:
        with SessionLocal() as session:
            movie = (
                session.query(DBMovie)
                .filter(DBMovie.id == movie_id)
                .first()
            )

            if not movie:
                return None

            for field, value in data.items():
                setattr(movie, field, value)

            session.commit()
            session.refresh(movie)

            return movie

    def delete(self, movie_id: int) -> bool:
        with SessionLocal() as session:
            movie = (
                session.query(DBMovie)
                .filter(DBMovie.id == movie_id)
                .first()
            )

            if not movie:
                return False

            session.delete(movie)
            session.commit()

            return True
