from typing import Protocol, Optional

from domain.models.userSignup import UserSignup
from domain.models.user import User


class IUserRepository(Protocol):
    def create_user(self, user: UserSignup) -> bool:
        ...

    def get_user_by_username(self, username: str) -> Optional[User]:
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        ...