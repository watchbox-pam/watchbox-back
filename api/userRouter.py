from fastapi import APIRouter, status
from fastapi.params import Depends
from starlette.exceptions import HTTPException
from typing import cast
import uuid

from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.userLogin import UserLogin
from domain.models.userSignup import UserSignup
from repository.playlist_repository import PlaylistRepository
from repository.user_repository import UserRepository
from domain.interfaces.services.i_playlist_service import IPlaylistService
from service.playlist_service import PlaylistService
from service.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service() -> IUserService:
    repository: IUserRepository = UserRepository()  # Implémentation concrète
    playlist_repository = PlaylistRepository()  # Implémentation concrète de IPlaylistRepository
    return UserService(repository, playlist_repository)


@user_router.post("/signup")
async def create_user(user: UserSignup, service: IUserService = Depends(get_user_service)):
    try:
        user_id = service.create_user(user)
        if user_id:
            return user_id
        else:
            raise HTTPException(status_code=400, detail="L'inscription a échoué")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@user_router.post("/login")
async def login_user(user: UserLogin, service: IUserService = Depends(get_user_service)):
    try:
        result = service.login_user(user)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="La connexion a échoué")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@user_router.get("/{id}")
async def get_user_by_id(id: str, service: IUserService = Depends(get_user_service)):
    try:
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(id)
            id_str = str(uuid_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format d'ID utilisateur invalide")

        user = service.get_user_by_id(id_str)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "country": user.country,
                "profile_picture_path": user.profile_picture_path,
                "banner_path": user.banner_path,
                "is_private": user.is_private,
                "history_private": user.history_private,
                "adult_content": user.adult_content,
                "last_connection": user.last_connection,
                "created_at": user.created_at
            }
        else:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))