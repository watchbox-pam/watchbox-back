from fastapi import APIRouter, status
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.userLogin import UserLogin
from domain.models.userSignup import UserSignup
from repository.user_repository import UserRepository
from service.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service() -> IUserService:
    repository: IUserRepository = UserRepository()
    return UserService(repository)


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
        user_id = service.login_user(user)
        if user_id:
            return user_id
        else:
            raise HTTPException(status_code=400, detail="La connexion a échoué")
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@user_router.get("/{id}")
async def get_user_by_id(id: str, service: IUserService = Depends(get_user_service)):
    ...