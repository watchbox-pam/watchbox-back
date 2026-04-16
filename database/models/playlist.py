from typing import Optional
import datetime
import uuid
from sqlalchemy import Boolean, DateTime, ForeignKeyConstraint, PrimaryKeyConstraint, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.user import User

class Playlist(Base):
    __tablename__ = 'playlist'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], name='playlist_user_id_fkey'),
        PrimaryKeyConstraint('id', name='playlist_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    user: Mapped['User'] = relationship('User', back_populates='playlist')
