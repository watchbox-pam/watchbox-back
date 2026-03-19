from fastapi import APIRouter, status
from fastapi.params import Depends
from starlette.exceptions import HTTPException
from typing import cast
import uuid

from api.auth.verify_auth_token import check_jwt_token
from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.userLogin import UserLogin
from domain.models.userPassword import UserPassword
from domain.models.userSignup import UserSignup
from domain.models.userVerification import UserVerification
from repository.playlist_repository import PlaylistRepository
from repository.user_repository import UserRepository
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


@user_router.get("/{id}", dependencies=[Depends(check_jwt_token)])
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
                "email": user.email,
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


@user_router.post("/verification")
async def verify_user(user_verification: UserVerification, service: IUserService = Depends(get_user_service)):
    try:
        if user_verification.code == "" or user_verification.token == "":
            return False
        verification_valid = service.verify_user(user_verification)
        return verification_valid
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@user_router.delete("/{id}")
async def delete_user(
    id: str,
    user_id: str = Depends(check_jwt_token),
    service: IUserService = Depends(get_user_service)
):

    try:
        try:
            uuid_obj = uuid.UUID(id)
            id_str = str(uuid_obj)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Format d'ID utilisateur invalide"
            )

        success = service.delete_user(id_str)

        if success:
            return {
                "message": "Compte supprimé avec succès",
                "deleted_user_id": id_str
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="La suppression a échoué"
            )

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@user_router.post("/forgot-password")
async def forgot_password(email: str, service: IUserService = Depends(get_user_service)):
    try:
        result = service.send_password_reset_email(email)
        return result
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@user_router.post("/reset-password")
async def reset_password(new_password: UserPassword, service: IUserService = Depends(get_user_service)):
    try:
        result = service.reset_user_password(new_password)
        return result
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))