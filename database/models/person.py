from typing import Optional
import datetime
from sqlalchemy import ARRAY, Boolean, Date, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.gender import Gender
    from database.models.tv import Tv

class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        ForeignKeyConstraint(['gender'], ['gender.value'], name='person_gender_fkey'),
        PrimaryKeyConstraint('id', name='person_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adult: Mapped[Optional[bool]] = mapped_column(Boolean)
    also_known_as: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String()))
    biography: Mapped[Optional[str]] = mapped_column(Text)
    birthday: Mapped[Optional[datetime.date]] = mapped_column(Date)
    deathday: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[int]] = mapped_column(Integer)
    homepage: Mapped[Optional[str]] = mapped_column(Text)
    imdb_id: Mapped[Optional[str]] = mapped_column(String)
    known_for_department: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)
    place_of_birth: Mapped[Optional[str]] = mapped_column(String)
    profile_path: Mapped[Optional[str]] = mapped_column(String)

    gender_: Mapped[Optional['Gender']] = relationship('Gender', back_populates='person')
    tv: Mapped[list['Tv']] = relationship('Tv', secondary='tv_created_by', back_populates='person')
