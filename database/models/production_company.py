from typing import Optional
from sqlalchemy import Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base

class ProductionCompany(Base):
    __tablename__ = 'production_company'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='production_company_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    logo_path: Mapped[Optional[str]] = mapped_column(Text)
    name: Mapped[Optional[str]] = mapped_column(String)
    origin_country: Mapped[Optional[str]] = mapped_column(String)
