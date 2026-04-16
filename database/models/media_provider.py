from typing import Optional
from sqlalchemy import Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base

class MediaProvider(Base):
    __tablename__ = 'media_provider'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='media_provider_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String)
    display_priority: Mapped[Optional[int]] = mapped_column(Integer)
