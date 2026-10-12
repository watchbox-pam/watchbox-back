import os
from hashlib import sha256
from uuid import UUID

from database.models import User as DBUser
from domain.interfaces.repositories.i_admin_user_repository import IAdminUserRepository
from domain.interfaces.services.i_admin_user_service import IAdminUserService
from domain.models.admin_errors import (
    AdminConfigurationError,
    AdminConflictError,
    AdminNotFoundError,
    AdminValidationError,
)
from domain.models.admin_user import AdminUserCreate, AdminUserUpdate


def _isoformat_or_none(value):
    return value.isoformat() if value else None


def _user_to_dict(user: DBUser, include_banner: bool = True) -> dict:
    result = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "country": user.country,
        "birthdate": _isoformat_or_none(user.birthdate),
        "profile_picture_path": user.profile_picture_path,
        "banner_path": user.banner_path,
        "is_private": user.is_private,
        "history_private": user.history_private,
        "adult_content": user.adult_content,
        "is_verified": user.is_verified,
        "last_connection": _isoformat_or_none(user.last_connection),
        "created_at": _isoformat_or_none(user.created_at),
    }

    if not include_banner:
        # La liste paginée ne renvoyait pas banner_path : on garde le même contrat
        del result["banner_path"]

    return result


class AdminUserService(IAdminUserService):
    def __init__(self, repository: IAdminUserRepository):
        self.repository = repository

    def get_users(self, page: int, limit: int) -> dict:
        offset = (page - 1) * limit

        total = self.repository.count()
        users = self.repository.find_page(offset, limit)

        return {
            "items": [
                _user_to_dict(user, include_banner=False)
                for user in users
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit,
            },
        }

    def get_user(self, user_id: UUID) -> dict:
        user = self.repository.find_by_id(user_id)

        if not user:
            raise AdminNotFoundError("Utilisateur introuvable")

        return _user_to_dict(user)

    def create_user(self, data: AdminUserCreate) -> dict:
        if self.repository.username_exists(data.username):
            raise AdminConflictError("Ce pseudo est déjà utilisé")

        if self.repository.email_exists(data.email):
            raise AdminConflictError("Cette adresse mail est déjà utilisée")

        pepper = os.getenv("PEPPER")

        if not pepper:
            raise AdminConfigurationError("Configuration PEPPER manquante")

        if len(data.salt) != 32:
            raise AdminValidationError(
                "Le salt doit contenir exactement 32 caractères"
            )

        # SHA256(firstHash + salt)
        salted_password = sha256(
            (data.password + data.salt).encode("utf-8")
        ).hexdigest()

        # SHA256(saltedPassword + pepper)
        hashed_password = sha256(
            (salted_password + pepper).encode("utf-8")
        ).hexdigest()

        user = self.repository.create_with_playlist({
            "username": data.username,
            "email": data.email,
            "password": hashed_password,
            "birthdate": data.birthdate,
            "salt": data.salt,
            "is_private": data.is_private,
            "history_private": data.history_private,
            "adult_content": data.adult_content,
            "is_verified": data.is_verified,
            "country": data.country,
            "profile_picture_path": data.profile_picture_path,
            "banner_path": data.banner_path,
        })

        return _user_to_dict(user)

    def update_user(self, user_id: UUID, data: AdminUserUpdate) -> dict:
        user = self.repository.update(
            user_id,
            data.model_dump(exclude_unset=True)
        )

        if not user:
            raise AdminNotFoundError("Utilisateur introuvable")

        return _user_to_dict(user)

    def delete_user(self, user_id: UUID) -> dict:
        if not self.repository.delete(user_id):
            raise AdminNotFoundError("Utilisateur introuvable")

        return {
            "success": True,
            "id": str(user_id)
        }
