from typing import Optional
import datetime
import uuid

from sqlalchemy import Boolean, Date, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.country import Country
    from database.models.playlist import Playlist

class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        ForeignKeyConstraint(['country'], ['country.iso'], name='user_country_fkey'),
        PrimaryKeyConstraint('id', name='user_pkey'),
        UniqueConstraint('email', name='user_email_key'),
        UniqueConstraint('username', name='user_username_key')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    birthdate: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    history_private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    adult_content: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    last_connection: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    salt: Mapped[str] = mapped_column(String(32), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    country: Mapped[Optional[str]] = mapped_column(String)
    profile_picture_path: Mapped[Optional[str]] = mapped_column(String(256), comment="Chemin vers l'image de profil de l'utilisateur")
    banner_path: Mapped[Optional[str]] = mapped_column(String(256), comment="Chemin vers la banniere de l'utilisateur")
    password_reset_token: Mapped[Optional[str]] = mapped_column(String)
    verification_code: Mapped[Optional[str]] = mapped_column(String)
    verification_code_token: Mapped[Optional[str]] = mapped_column(String)

    country_: Mapped[Optional['Country']] = relationship('Country', back_populates='user')
    playlist: Mapped[list['Playlist']] = relationship('Playlist', back_populates='user', cascade='all, delete-orphan')
