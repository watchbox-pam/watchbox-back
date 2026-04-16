from sqlalchemy import Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.movie import Movie
    
class MovieGenre(Base):
    __tablename__ = 'movie_genre'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='movie_genre_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    movie: Mapped[list['Movie']] = relationship('Movie', secondary='movie_movie_genre', back_populates='genre')
