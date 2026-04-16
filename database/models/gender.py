from sqlalchemy import Integer, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.person import Person

class Gender(Base):
    __tablename__ = 'gender'
    __table_args__ = (
        PrimaryKeyConstraint('value', name='gender_pkey'),
        UniqueConstraint('gender', name='gender_gender_key')
    )

    value: Mapped[int] = mapped_column(Integer, primary_key=True)
    gender: Mapped[str] = mapped_column(String, nullable=False)

    person: Mapped[list['Person']] = relationship('Person', back_populates='gender_')
