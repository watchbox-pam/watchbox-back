from typing import Optional
import datetime
from sqlalchemy import BigInteger, Boolean, Date, Double, Integer, PrimaryKeyConstraint, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.movie_genre import MovieGenre

class Movie(Base):
    __tablename__ = 'movie'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='movie_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adult: Mapped[Optional[bool]] = mapped_column(Boolean)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String)
    budget: Mapped[Optional[int]] = mapped_column(Integer)
    homepage: Mapped[Optional[str]] = mapped_column(Text)
    imdb_id: Mapped[Optional[str]] = mapped_column(String)
    original_language: Mapped[Optional[str]] = mapped_column(String)
    original_title: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    poster_path: Mapped[Optional[str]] = mapped_column(Text)
    release_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    revenue: Mapped[Optional[int]] = mapped_column(BigInteger)
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String)
    tagline: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String)
    popularity: Mapped[Optional[float]] = mapped_column(Double(53))
    video: Mapped[Optional[str]] = mapped_column(String)
    infos_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    genre: Mapped[list['MovieGenre']] = relationship('MovieGenre', secondary='movie_movie_genre', back_populates='movie')
