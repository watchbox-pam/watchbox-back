from typing import Optional
import datetime
from sqlalchemy import Integer, String, Text, text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.language import Language
    from database.models.movie import Movie

class MovieTranslation(Base):
    __tablename__ = 'movie_translation'
    __table_args__ = (
        UniqueConstraint('movie_id', 'language_iso', name='movie_translation_movie_id_language_iso_key'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[int] = mapped_column(
        ForeignKey('movie.id', ondelete='CASCADE'),
        nullable=False
    )
    language_iso: Mapped[str] = mapped_column(
        ForeignKey('language.iso'),
        nullable=False
    )
    overview: Mapped[Optional[str]] = mapped_column(Text)
    poster_path: Mapped[Optional[str]] = mapped_column(Text)
    tagline: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("now()"))
    language: Mapped['Language'] = relationship('Language', back_populates='movie_translations')
    movie: Mapped['Movie'] = relationship('Movie', back_populates='translations')
