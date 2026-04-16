from typing import Optional
import datetime
from sqlalchemy import ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.tv_season import TvSeason
    
class TvEpisode(Base):
    __tablename__ = 'tv_episode'
    __table_args__ = (
        ForeignKeyConstraint(['season_id'], ['tv_season.id'], name='tv_episode_season_id_fkey'),
        PrimaryKeyConstraint('id', name='tv_episode_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    episode_number: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    production_code: Mapped[Optional[str]] = mapped_column(String)
    runtime: Mapped[Optional[int]] = mapped_column(Integer)
    still_path: Mapped[Optional[str]] = mapped_column(String)
    season_id: Mapped[Optional[str]] = mapped_column(String)

    season: Mapped[Optional['TvSeason']] = relationship('TvSeason', back_populates='tv_episode')
