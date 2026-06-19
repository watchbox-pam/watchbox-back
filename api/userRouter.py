from fastapi import APIRouter
from fastapi.params import Depends
from starlette.exceptions import HTTPException
from pydantic import BaseModel
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


@user_router.get("/profile/{user_id}")
async def get_user_by_id(user_id: str, service: IUserService = Depends(get_user_service)):
    try:
        id_str: str = str(user_id)
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
                "birthdate": user.birthdate,
                "last_connection": user.last_connection,
                "created_at": user.created_at
            }
        else:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    except HTTPException as error:
        print(f"error 2 is {error}")
        raise
    except Exception as error:
        print(f"error 3 is {error}")
        raise HTTPException(status_code=400, detail=str(error))

@user_router.get("/allUsers", dependencies=[Depends(check_jwt_token)])
async def get_all_users(service: IUserService = Depends(get_user_service)):
    try:
        users = service.get_all_users()
        return users
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


@user_router.delete("")
async def delete_user(
    user_id: str = Depends(check_jwt_token),
    service: IUserService = Depends(get_user_service)
):

    try:
        id_str: str = str(user_id)
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

class UpdateSettingsRequest(BaseModel):
    adult_content: bool
    is_private: bool
    history_private: bool

@user_router.patch("/settings")
async def update_settings(
    request: UpdateSettingsRequest,
    user_id: str = Depends(check_jwt_token),
    service: IUserService = Depends(get_user_service)
):
    success = service.update_settings(user_id, request.adult_content, request.is_private, request.history_private)
    if not success:
        raise HTTPException(status_code=400, detail="Mise à jour des paramètres échouée")
    return {"success": True}


class ForgotPasswordRequest(BaseModel):
    email: str

@user_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, service: IUserService = Depends(get_user_service)):
    try:
        result = service.send_password_reset_email(request.email)
        return result
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


class CheckPasswordResetTokenRequest(BaseModel):
    token: str

@user_router.post("/check-password-reset-token")
async def forgot_password(request: CheckPasswordResetTokenRequest, service: IUserService = Depends(get_user_service)):
    try:
        result = service.check_password_reset_token(request.token)
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


@user_router.get("/password_reset_token")
async def get_reset_password_token(user_id: str = Depends(check_jwt_token), service: IUserService = Depends(get_user_service)):
    try:
        result = service.get_password_reset_token(user_id)
        return result
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))