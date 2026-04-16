from sqlalchemy import Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base

class Keyword(Base):
    __tablename__ = 'keyword'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='keyword_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

