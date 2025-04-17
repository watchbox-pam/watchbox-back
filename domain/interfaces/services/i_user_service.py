from typing import Protocol, Optional

from domain.models.user import User
from domain.models.userLogin import UserLogin
from domain.models.userSignup import UserSignup


class IUserService(Protocol):
    def create_user(self, user: UserSignup) -> Optional[str]:
        ...

    def get_user_by_username(self, username: str) -> Optional[User]:
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        ...

    def login_user(self, user: UserLogin) -> dict[str, str]:
        ...

    def get_user_by_id(self, id: str) -> Optional[User]:
        ...