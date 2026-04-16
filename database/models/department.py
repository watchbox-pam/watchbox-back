from sqlalchemy import Identity, Integer, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.job import Job

class Department(Base):
    __tablename__ = 'department'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='department_pkey'),
        UniqueConstraint('name', name='department_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    job: Mapped[list['Job']] = relationship('Job', back_populates='department')

