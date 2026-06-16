from typing import Optional
from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.movie_translation import MovieTranslation

class Language(Base):
    __tablename__ = 'language'
    __table_args__ = (
        PrimaryKeyConstraint('iso', name='language_pkey'),
    )

    iso: Mapped[str] = mapped_column(String, primary_key=True)
    english_name: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)
    movie_translations: Mapped[list['MovieTranslation']] = relationship('MovieTranslation', back_populates='language')