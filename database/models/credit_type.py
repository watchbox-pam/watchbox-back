from sqlalchemy import Identity, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base

class CreditType(Base):
    __tablename__ = 'credit_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='credit_type_pkey'),
        UniqueConstraint('name', name='credit_type_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)