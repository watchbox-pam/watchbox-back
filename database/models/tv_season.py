from typing import Optional
import datetime
from sqlalchemy import ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.tv import Tv
    from database.models.tv_episode import TvEpisode

class TvSeason(Base):
    __tablename__ = 'tv_season'
    __table_args__ = (
        ForeignKeyConstraint(['tv_id'], ['tv.id'], name='tv_season_tv_id_fkey'),
        PrimaryKeyConstraint('id', name='tv_season_pkey')
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    air_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    name: Mapped[Optional[str]] = mapped_column(String)
    overview: Mapped[Optional[str]] = mapped_column(Text)
    poster_path: Mapped[Optional[str]] = mapped_column(String)
    season_number: Mapped[Optional[int]] = mapped_column(Integer)
    tv_id: Mapped[Optional[int]] = mapped_column(Integer)

    tv: Mapped[Optional['Tv']] = relationship('Tv', back_populates='tv_season')
    tv_episode: Mapped[list['TvEpisode']] = relationship('TvEpisode', back_populates='season')
