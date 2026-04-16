from typing import Optional
from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base

class Language(Base):
    __tablename__ = 'language'
    __table_args__ = (
        PrimaryKeyConstraint('iso', name='language_pkey'),
    )

    iso: Mapped[str] = mapped_column(String, primary_key=True)
    english_name: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(String)
