from typing import Optional
from sqlalchemy import ForeignKeyConstraint, Identity, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.department import Department

class Job(Base):
    __tablename__ = 'job'
    __table_args__ = (
        ForeignKeyConstraint(['department_id'], ['department.id'], name='job_department_id_fkey'),
        PrimaryKeyConstraint('id', name='job_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(Integer)

    department: Mapped[Optional['Department']] = relationship('Department', back_populates='job')