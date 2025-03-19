from fastapi import APIRouter
from fastapi.params import Depends
from starlette.exceptions import HTTPException

from domain.interfaces.repositories.i_user_repository import IUserRepository
from domain.interfaces.services.i_user_service import IUserService
from domain.models.userSignup import UserSignup
from repository.user_repository import UserRepository
from service.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service() -> IUserService:
    repository: IUserRepository = UserRepository()
    return UserService(repository)


@user_router.post("/")
async def create_user(user: UserSignup, service: IUserService = Depends(get_user_service)):
    user_id = service.create_user(user)
    if user_id:
        return user_id
    else:
        raise HTTPException(status_code=400, detail="User not inserted")