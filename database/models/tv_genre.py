from sqlalchemy import Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.tv import Tv
    
class TvGenre(Base):
    __tablename__ = 'tv_genre'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tv_genre_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    tv: Mapped[list['Tv']] = relationship('Tv', secondary='tv_tv_genre', back_populates='genre')