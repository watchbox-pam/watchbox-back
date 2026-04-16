from sqlalchemy import Boolean, PrimaryKeyConstraint, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.user import User

class Country(Base):
    __tablename__ = 'country'
    __table_args__ = (
        PrimaryKeyConstraint('iso', name='country_pkey'),
        UniqueConstraint('name', name='country_name_key')
    )

    iso: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    exists: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))

    user: Mapped[list['User']] = relationship('User', back_populates='country_')