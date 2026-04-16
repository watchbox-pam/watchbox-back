from typing import Optional
import datetime
from sqlalchemy import ARRAY, Boolean, Date, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.tv_genre import TvGenre
    from database.models.person import Person
    from database.models.tv_season import TvSeason

class Tv(Base):
    __tablename__ = 'tv'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tv_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adult: Mapped[Optional[bool]] = mapped_column(Boolean)
    backdrop_path: Mapped[Optional[str]] = mapped_column(String)
    episode_run_time: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()))
    first_air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    homepage: Mapped[Optional[str]] = mapped_column(Text)
    in_production: Mapped[Optional[bool]] = mapped_column(Boolean)
    languages: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    last_air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    name: Mapped[Optional[str]] = mapped_column(String)
    number_of_episodes: Mapped[Optional[int]] = mapped_column(Integer)
    number_of_seasons: Mapped[Optional[int]] = mapped_column(Integer)
    origin_country: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    original_language: Mapped[Optional[str]] = mapped_column(String)
    original_name: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    poster_path: Mapped[Optional[str]] = mapped_column(Text)
    release_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    revenue: Mapped[Optional[int]] = mapped_column(Integer)
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String)
    tagline: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(String)
    video: Mapped[Optional[bool]] = mapped_column(Boolean)

    genre: Mapped[list['TvGenre']] = relationship('TvGenre', secondary='tv_tv_genre', back_populates='tv')
    person: Mapped[list['Person']] = relationship('Person', secondary='tv_created_by', back_populates='tv')
    tv_season: Mapped[list['TvSeason']] = relationship('TvSeason', back_populates='tv')
