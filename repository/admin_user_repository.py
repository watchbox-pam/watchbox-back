import datetime
import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy import func

from database.db import SessionLocal
from database.models import Playlist as DBPlaylist
from database.models import User as DBUser
from domain.interfaces.repositories.i_admin_user_repository import IAdminUserRepository


class AdminUserRepository(IAdminUserRepository):
    def count(self) -> int:
        with SessionLocal() as session:
            return session.query(func.count(DBUser.id)).scalar() or 0

    def find_page(self, offset: int, limit: int) -> list[DBUser]:
        with SessionLocal() as session:
            return (
                session.query(DBUser)
                .order_by(DBUser.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

    def find_by_id(self, user_id: UUID) -> Optional[DBUser]:
        with SessionLocal() as session:
            return (
                session.query(DBUser)
                .filter(DBUser.id == user_id)
                .first()
            )

    def username_exists(self, username: str) -> bool:
        with SessionLocal() as session:
            return (
                session.query(DBUser.id)
                .filter(DBUser.username == username)
                .first()
                is not None
            )

    def email_exists(self, email: str) -> bool:
        with SessionLocal() as session:
            return (
                session.query(DBUser.id)
                .filter(DBUser.email == email)
                .first()
                is not None
            )

    def create_with_playlist(self, data: dict) -> DBUser:
        """Crée l'utilisateur et sa playlist par défaut dans la même transaction."""
        with SessionLocal() as session:
            now = datetime.datetime.now()

            user = DBUser(
                **data,
                id=uuid.uuid4(),
                last_connection=now,
                created_at=now,
                password_reset_token=None,
                verification_code=None,
                verification_code_token=None,
                country_=None,
                playlist=[],
            )

            session.add(user)

            playlist = DBPlaylist(
                id=uuid.uuid4(),
                user_id=user.id,
                title="Ma playlist",
                is_private=True,
                created_at=now,
                user=user,
            )

            session.add(playlist)

            session.commit()
            session.refresh(user)

            return user

    def update(self, user_id: UUID, data: dict) -> Optional[DBUser]:
        with SessionLocal() as session:
            user = (
                session.query(DBUser)
                .filter(DBUser.id == user_id)
                .first()
            )

            if not user:
                return None

            for field, value in data.items():
                setattr(user, field, value)

            session.commit()
            session.refresh(user)

            return user

    def delete(self, user_id: UUID) -> bool:
        with SessionLocal() as session:
            user = (
                session.query(DBUser)
                .filter(DBUser.id == user_id)
                .first()
            )

            if not user:
                return False

            session.delete(user)
            session.commit()

            return True
